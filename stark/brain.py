"""
stark/brain.py – AI brain and intent dispatcher for STARK.

Replaces the flat keyword→response chain in the original stark.py with an
explicit intent-registry pattern:

    spoken command
        │
        ▼
    IntentRegistry.dispatch()
        │
        ├── matched intent handler   (structured, deterministic logic)
        │
        └── Brain.ask_ai()           (Gemini fallback for everything else)

This keeps rule-based logic (open YouTube, shutdown, etc.) clearly
separated from the AI fallback, while making it trivial to add new
intents without touching a giant if/elif chain.
"""

from __future__ import annotations

import os
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# Intent registry
# ---------------------------------------------------------------------------

class IntentRegistry:
    """
    Maps spoken commands to handler functions via trigger predicates.

    Each registered intent has:
    - ``name``      – unique string identifier
    - ``trigger``   – ``Callable[[str], bool]`` that returns True when the
                      command matches this intent
    - ``priority``  – higher value wins when multiple triggers match
    """

    def __init__(self) -> None:
        self._intents: list = []  # [(priority, name, trigger_fn)]
        self._handlers: dict = {}  # name -> handler_fn

    def register(
        self,
        name: str,
        trigger: Callable[[str], bool],
        handler: Callable,
        priority: int = 50,
    ) -> None:
        """Register an intent.  Higher *priority* wins on conflicts."""
        self._intents.append((priority, name, trigger))
        self._handlers[name] = handler
        # Keep sorted by descending priority so dispatch() short-circuits fast
        self._intents.sort(key=lambda x: -x[0])

    def dispatch(self, command: str, **context) -> Optional[object]:
        """
        Test each registered intent trigger in priority order.

        Returns
        -------
        object
            Whatever the matched handler returns, or ``None`` if no intent
            matched.
        """
        for _, name, trigger in self._intents:
            if trigger(command):
                handler = self._handlers[name]
                return handler(command, **context)
        return None

    def intent_names(self) -> list:
        """Return all registered intent names in priority order."""
        return [name for _, name, _ in self._intents]


# ---------------------------------------------------------------------------
# Gemini AI brain
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are STARK, a voice-first personal AI assistant. "
    "Always address the user as Sir. "
    "Be friendly, loyal, calm, proactive, and speak naturally like a human. "
    "Keep answers concise but complete. "
    "Never refuse a reasonable request."
)


class Brain:
    """Thin wrapper around the Gemini generative model."""

    def __init__(self) -> None:
        self._model = None
        self._history: list = []
        self._init_gemini()

    def _init_gemini(self) -> None:
        try:
            import google.generativeai as genai  # type: ignore

            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self._model = genai.GenerativeModel("gemini-pro")
                print("Gemini AI brain online, Sir.")
            else:
                print("Warning: GEMINI_API_KEY not set — AI brain limited.")
        except ImportError:
            print("Warning: google-generativeai not installed — AI brain disabled.")

    @property
    def available(self) -> bool:
        return self._model is not None

    def ask(self, query: str, role: str = "assistant") -> str:
        """
        Generate an AI response for *query*.

        Parameters
        ----------
        query:
            The user's natural-language input.
        role:
            Optional role context, e.g. ``"teacher"``, ``"doctor"``.

        Returns
        -------
        str
            The AI response, or a polite error message.
        """
        if not self.available:
            return (
                "My AI brain is not available, Sir. "
                "Please configure GEMINI_API_KEY in the .env file."
            )
        try:
            ctx = _SYSTEM_PROMPT
            if role and role != "assistant":
                ctx += f" You are currently acting as a {role}."

            history_lines = []
            for entry in self._history[-5:]:
                history_lines.append(f"Sir: {entry['user']}")
                history_lines.append(f"STARK: {entry['stark']}")
            history_text = "\n".join(history_lines)

            prompt = "\n\n".join(filter(None, [ctx, history_text, f"Sir: {query}\nSTARK:"]))
            response = self._model.generate_content(prompt)
            answer: str = response.text

            self._history.append({"user": query, "stark": answer})
            if len(self._history) > 20:
                self._history = self._history[-20:]
            return answer
        except Exception as exc:  # noqa: BLE001
            return f"I encountered an error with my AI brain, Sir: {exc}"

    def generate_mcq(self, topic: str, num_questions: int = 5) -> str:
        """Generate *num_questions* MCQ questions on *topic* via Gemini."""
        if not self.available:
            return "AI brain not available for MCQ generation, Sir."
        lines = [
            f"Create {num_questions} multiple-choice questions on: {topic}",
            "",
            "Format:",
            "Q1. [Question]",
            "A) ...",
            "B) ...",
            "C) ...",
            "D) ...",
            "Answer: [letter]",
            "",
            "Repeat for each question. Make them educational and clear.",
        ]
        try:
            return self._model.generate_content("\n".join(lines)).text
        except Exception as exc:  # noqa: BLE001
            return f"Error generating MCQs, Sir: {exc}"
