"""
stark/planner.py – Goal-oriented planner for STARK.

Current capability (Phase 1)
-----------------------------
Decomposes a high-level goal into an ordered list of actionable steps using
either the Gemini AI brain or a set of built-in rule-based templates when
the brain is unavailable.

Future capability (Phase 2 — not yet implemented)
--------------------------------------------------
Full agent loop::

    Goal
      │
      ▼
    Plan  (this module)
      │
      ▼
    Tool selection  → TaskManager / StudyModule / MemoryStore / Calendar …
      │
      ▼
    Execution  → each step dispatched through IntentRegistry
      │
      ▼
    Verify  → confirm outcome and report back to Sir

Example (Phase 1)
-----------------
>>> from stark.brain import Brain
>>> from stark.planner import Planner
>>> planner = Planner(Brain())
>>> steps = planner.plan("prepare for my math exam")
>>> for s in steps:
...     print(s)
1. Review the syllabus and list all topics.
2. Create a day-by-day study timetable.
3. Study each topic using the STARK study module.
4. Generate MCQ practice questions for each topic.
5. Schedule daily exam reminders.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .brain import Brain


# ---------------------------------------------------------------------------
# Rule-based plan templates
# Used when the AI brain is unavailable (no API key / offline).
# ---------------------------------------------------------------------------

_PLAN_TEMPLATES: dict = {
    "exam": [
        "List all topics in the syllabus.",
        "Create a day-by-day study timetable using the STARK study module.",
        "Study each topic systematically, starting with the least familiar.",
        "Generate MCQ practice questions for each topic.",
        "Schedule daily exam reminders.",
        "Do a full revision 2 days before the exam.",
    ],
    "project": [
        "Define the project goal and success criteria.",
        "Break the project into milestones.",
        "List the tasks required for each milestone.",
        "Schedule each task with deadlines.",
        "Track progress daily and adjust the plan as needed.",
    ],
    "health": [
        "Note current health concern or goal.",
        "Set a daily reminder for medication or exercise.",
        "Schedule a check-in reminder every week.",
        "Log progress in STARK memory.",
    ],
    "travel": [
        "Confirm destination and travel dates.",
        "Research best hotels and transport options.",
        "List must-see places and restaurants.",
        "Create a day-by-day itinerary.",
        "Set reminders for bookings and check-in times.",
    ],
    "default": [
        "Clarify the goal and desired outcome.",
        "Break the goal into smaller, manageable tasks.",
        "Prioritise tasks by importance and urgency.",
        "Schedule each task and set reminders.",
        "Review progress regularly and adapt.",
    ],
}

# Keywords that map a goal to a template
_TEMPLATE_KEYWORDS: dict[str, tuple] = {
    "exam":    ("exam", "study", "test", "syllabus", "preparation"),
    "project": ("project", "build", "develop", "launch", "feature"),
    "health":  ("health", "medicine", "exercise", "diet", "fitness", "doctor"),
    "travel":  ("travel", "trip", "holiday", "vacation", "visit"),
}


def _choose_template(goal: str) -> list:
    """Pick the best rule-based template for *goal*."""
    goal_lower = goal.lower()
    for key, keywords in _TEMPLATE_KEYWORDS.items():
        if any(kw in goal_lower for kw in keywords):
            return _PLAN_TEMPLATES[key]
    return _PLAN_TEMPLATES["default"]


# ---------------------------------------------------------------------------
# Planner
# ---------------------------------------------------------------------------

class Planner:
    """
    Decomposes a high-level *goal* into an ordered list of actionable steps.

    Parameters
    ----------
    brain:
        A ``stark.brain.Brain`` instance used for AI-powered decomposition.
        When the brain is unavailable (no API key), rule-based templates
        are used instead.
    """

    def __init__(self, brain: "Brain") -> None:
        self._brain = brain

    def plan(self, goal: str) -> list:
        """
        Return a list of step strings for the given *goal*.

        Tries Gemini first; falls back to rule-based templates on failure.
        """
        if self._brain.available:
            ai_steps = self._plan_with_ai(goal)
            if ai_steps:
                return ai_steps
        return _choose_template(goal)

    def plan_as_text(self, goal: str) -> str:
        """Return the plan as a numbered string (convenient for ``speak()``)."""
        steps = self.plan(goal)
        lines = [f"{i}. {s}" for i, s in enumerate(steps, 1)]
        return f"Here is my plan for '{goal}', Sir:\n" + "\n".join(lines)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _plan_with_ai(self, goal: str) -> list:
        """Ask Gemini to decompose *goal* into numbered steps.

        Returns an empty list if the AI call fails or produces no output.
        """
        prompt = (
            f"You are STARK, a personal AI assistant. "
            f"Break down the following goal into 5–7 clear, actionable steps. "
            f"Return ONLY a numbered list, one step per line.\n\n"
            f"Goal: {goal}"
        )
        try:
            raw = self._brain.generate_content(prompt)
            if not raw:
                return []
            steps = []
            for line in raw.splitlines():
                line = line.strip()
                # Accept lines like "1. Step text" or "- Step text"
                if line and (line[0].isdigit() or line.startswith("-")):
                    text = line.lstrip("0123456789.-) ").strip()
                    if text:
                        steps.append(text)
            return steps if steps else []
        except Exception:  # noqa: BLE001 – fall through to template
            return []
