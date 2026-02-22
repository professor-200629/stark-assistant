"""
stark/core.py – Canonical StarkAssistant orchestrator.

This is the ONE source of truth for STARK's logic.  The old flat
keyword→response chain has been replaced with an intent-registry pattern
(see stark/brain.py) so that adding a new capability never requires
editing a giant if/elif ladder.

Architecture:

    spoken command
         │
         ▼
    StarkAssistant.process_command()
         │
         ├─ IntentRegistry.dispatch()   → matched handler (deterministic)
         │
         └─ Brain.ask()                 → Gemini (catch-all)
"""

from __future__ import annotations

import datetime
import os
import random
import webbrowser
from typing import Optional

from dotenv import load_dotenv

from .brain import Brain, IntentRegistry
from .memory_store import MemoryStore
from .planner import Planner
from .voice import listen, speak
from .automation import execute_action

load_dotenv()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _contains_any(command: str, words: tuple) -> bool:
    return any(w in command for w in words)


# ---------------------------------------------------------------------------
# StarkAssistant
# ---------------------------------------------------------------------------

class StarkAssistant:
    """
    Central STARK orchestrator.

    Each *intent* is a (trigger, handler) pair registered in
    ``self._registry``.  Commands that match no intent fall through to the
    Gemini AI brain.
    """

    _KNOWN_SITES: dict = {
        "youtube": "https://youtube.com",
        "google": "https://google.com",
        "facebook": "https://facebook.com",
        "twitter": "https://twitter.com",
        "instagram": "https://instagram.com",
        "github": "https://github.com",
        "gmail": "https://gmail.com",
        "netflix": "https://netflix.com",
        "amazon": "https://amazon.com",
        "whatsapp": "https://web.whatsapp.com",
        "wikipedia": "https://wikipedia.org",
        "hotstar": "https://hotstar.com",
        "prime": "https://primevideo.com",
    }

    def __init__(self) -> None:
        self.current_role: str = "assistant"
        self.memory: MemoryStore = MemoryStore()
        self.exam_schedule: dict = {}
        self.study_timetable: dict = {}
        self.busy: bool = False
        self.busy_message: str = (
            "Balu is busy right now. I am STARK, his personal AI assistant. "
            "If it is urgent, please leave a message and I will inform him. "
            "For emergencies, please say emergency and I will notify him immediately."
        )
        self.missed_calls: dict = {}
        self.work_start_time: Optional[datetime.datetime] = None

        self._brain = Brain()
        self._planner = Planner(self._brain)
        self._registry = IntentRegistry()
        self._register_intents()
        self._greet()

    # ------------------------------------------------------------------
    # Startup
    # ------------------------------------------------------------------

    def _greet(self) -> None:
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            speak("Good morning, Sir! STARK is online and ready to serve you.")
        elif 12 <= hour < 17:
            speak("Good afternoon, Sir! How may I assist you today?")
        elif 17 <= hour < 21:
            speak("Good evening, Sir! STARK at your service.")
        else:
            speak("Hello, Sir. STARK is online. Working late tonight?")

    # ------------------------------------------------------------------
    # Intent registration
    # ------------------------------------------------------------------

    def _register_intents(self) -> None:
        """Register all built-in intents in priority order."""
        reg = self._registry

        # High-priority: exit (priority 100)
        reg.register(
            "exit",
            lambda c: _contains_any(c, ("goodbye", "bye", "exit", "quit", "sleep")),
            self._handle_exit,
            priority=100,
        )

        # Greetings (90)
        reg.register(
            "greeting",
            lambda c: _contains_any(c, ("hello", "hi", "hey stark", "good morning", "good evening")),
            self._handle_greeting,
            priority=90,
        )

        # Busy mode (80)
        reg.register(
            "busy_on",
            lambda c: _contains_any(c, ("busy mode on", "i am busy", "set busy")),
            self._handle_busy_on,
            priority=80,
        )
        reg.register(
            "busy_off",
            lambda c: _contains_any(c, ("busy mode off", "i am free", "not busy")),
            self._handle_busy_off,
            priority=80,
        )

        # System controls – destructive (75, PIN-guarded in automation.py)
        reg.register(
            "shutdown",
            lambda c: _contains_any(c, ("shutdown", "shut down")),
            self._handle_shutdown,
            priority=75,
        )
        reg.register(
            "restart",
            lambda c: _contains_any(c, ("restart", "reboot")),
            self._handle_restart,
            priority=75,
        )

        # System controls – non-destructive (70)
        reg.register(
            "lock",
            lambda c: "lock" in c and "unlock" not in c,
            lambda c, **_: self._sys("lock"),
            priority=70,
        )
        reg.register(
            "volume_up",
            lambda c: _contains_any(c, ("increase volume", "volume up")),
            lambda c, **_: self._sys("volume_up"),
            priority=70,
        )
        reg.register(
            "volume_down",
            lambda c: _contains_any(c, ("decrease volume", "volume down", "mute")),
            lambda c, **_: self._sys("volume_down"),
            priority=70,
        )
        reg.register(
            "brightness_up",
            lambda c: _contains_any(c, ("increase brightness", "brightness up")),
            lambda c, **_: self._sys("brightness_up"),
            priority=70,
        )
        reg.register(
            "brightness_down",
            lambda c: _contains_any(c, ("decrease brightness", "brightness down")),
            lambda c, **_: self._sys("brightness_down"),
            priority=70,
        )

        # Camera (65)
        reg.register(
            "camera_live",
            lambda c: _contains_any(c, ("open camera", "show camera", "camera on")),
            lambda c, **_: self.access_camera(),
            priority=65,
        )
        reg.register(
            "camera_photo",
            lambda c: _contains_any(c, ("take photo", "take picture", "click photo")),
            lambda c, **_: self.take_photo(),
            priority=65,
        )

        # YouTube / media (60)
        reg.register(
            "youtube",
            lambda c: _contains_any(c, ("play", "youtube", "trailer", "song", "music video")),
            self._handle_youtube,
            priority=60,
        )

        # Open website (55)
        reg.register(
            "open_site",
            lambda c: c.startswith("open "),
            self._handle_open_site,
            priority=55,
        )

        # Messaging (50)
        reg.register(
            "send_message",
            lambda c: "send" in c and _contains_any(c, ("whatsapp", "message", "text")),
            self._handle_send_message,
            priority=50,
        )

        # Study tools (45)
        reg.register(
            "timetable",
            lambda c: _contains_any(c, ("create timetable", "study timetable", "exam timetable")),
            self._handle_timetable,
            priority=45,
        )
        reg.register(
            "mcq",
            lambda c: _contains_any(c, ("mcq", "multiple choice", "generate questions")),
            self._handle_mcq,
            priority=45,
        )
        reg.register(
            "todo",
            lambda c: _contains_any(c, ("to do", "todo", "task list")),
            self._handle_todo,
            priority=45,
        )

        # Work session (40)
        reg.register(
            "start_work",
            lambda c: _contains_any(c, ("start work", "start session")),
            lambda c, **_: self.start_work_session(),
            priority=40,
        )

        # Time / date (40)
        reg.register(
            "tell_time",
            lambda c: "time" in c and "timetable" not in c,
            self._handle_time,
            priority=40,
        )
        reg.register(
            "tell_date",
            lambda c: "date" in c,
            self._handle_date,
            priority=40,
        )

        # Memory (35)
        reg.register(
            "remember",
            lambda c: "remember" in c,
            self._handle_remember,
            priority=35,
        )
        reg.register(
            "recall",
            lambda c: _contains_any(c, ("what do you know", "what do you remember")),
            self._handle_recall,
            priority=35,
        )

        # Role change (30)
        reg.register(
            "role_change",
            lambda c: _contains_any(c, ("act as", "switch to")),
            self._handle_role_change,
            priority=30,
        )

        # Reminders (25)
        reg.register(
            "reminder",
            lambda c: _contains_any(c, ("remind me", "set reminder")),
            self._handle_reminder,
            priority=25,
        )

        # Goal planning (22) — decomposes a high-level goal into steps
        reg.register(
            "plan",
            lambda c: _contains_any(c, ("plan ", "create plan", "make plan", "help me plan", "plan my")),
            self._handle_plan,
            priority=22,
        )

        # Domain-specific AI roles (20 – routes to Gemini with role context)
        reg.register(
            "education",
            lambda c: _contains_any(c, (
                "explain", "what is", "how does", "how to", "teach me",
                "tell me about", "solve", "answer", "define",
            )),
            lambda c, **_: speak(self._brain.ask(c, role=self.current_role or "teacher")),
            priority=20,
        )
        reg.register(
            "health",
            lambda c: _contains_any(c, ("health", "doctor", "medicine", "sick", "pain", "tired")),
            lambda c, **_: speak(self._brain.ask(c, role="doctor")),
            priority=20,
        )
        reg.register(
            "travel",
            lambda c: _contains_any(c, ("travel", "hotel", "restaurant", "tourist", "visit")),
            lambda c, **_: speak(self._brain.ask(c, role="travel guide")),
            priority=20,
        )
        reg.register(
            "entertainment",
            lambda c: _contains_any(c, ("movie", "show", "recommend", "suggest")),
            lambda c, **_: speak(self._brain.ask(c, role="entertainment advisor")),
            priority=20,
        )

    # ------------------------------------------------------------------
    # Intent handlers
    # ------------------------------------------------------------------

    def _handle_exit(self, command: str, **_) -> bool:
        speak("Goodbye, Sir. It has been a pleasure serving you. STARK going offline.")
        return False  # signals main loop to stop

    def _handle_greeting(self, command: str, **_) -> bool:
        speak(random.choice([
            "Hello, Sir! How may I assist you today?",
            "Hi there, Sir! What can I do for you?",
            "Good to hear from you, Sir! How can I help?",
        ]))
        return True

    def _handle_busy_on(self, command: str, **_) -> bool:
        self.set_busy(True)
        return True

    def _handle_busy_off(self, command: str, **_) -> bool:
        self.set_busy(False)
        return True

    def _handle_shutdown(self, command: str, **_) -> bool:
        speak("Are you sure you want to shut down the system, Sir?")
        confirm = listen(timeout=5)
        if confirm and "yes" in confirm:
            execute_action("shutdown", speak_fn=speak, listen_fn=listen)
        else:
            speak("Shutdown cancelled, Sir.")
        return True

    def _handle_restart(self, command: str, **_) -> bool:
        speak("Are you sure you want to restart, Sir?")
        confirm = listen(timeout=5)
        if confirm and "yes" in confirm:
            execute_action("restart", speak_fn=speak, listen_fn=listen)
        else:
            speak("Restart cancelled, Sir.")
        return True

    def _sys(self, action: str) -> bool:
        """Execute a non-destructive system action."""
        execute_action(action, speak_fn=speak, listen_fn=listen)
        return True

    def _handle_youtube(self, command: str, **_) -> bool:
        query = command
        for noise in ("stark", "play", "on youtube", "youtube", "in", "trailer",
                      "song", "music video", "please", "open"):
            query = query.replace(noise, "").strip()
        if query:
            self.open_youtube(query)
        else:
            speak("What would you like me to play, Sir?")
        return True

    def _handle_open_site(self, command: str, **_) -> bool:
        for name, url in self._KNOWN_SITES.items():
            if name in command:
                self.open_website(url)
                return True
        # Try to extract a bare domain from the command
        for word in command.split():
            if "." in word and len(word) > 3:
                self.open_website(word)
                return True
        speak(self._brain.ask(command))
        return True

    def _handle_send_message(self, command: str, **_) -> bool:
        speak("Please say the phone number with country code, Sir.")
        phone = listen(timeout=10)
        speak("What is the message, Sir?")
        msg = listen(phrase_time_limit=20)
        if phone and msg:
            result = self.send_whatsapp_message(phone.replace(" ", ""), msg)
            speak(result)
        else:
            speak("I could not capture all the details, Sir. Please try again.")
        return True

    def _handle_timetable(self, command: str, **_) -> bool:
        speak("Please tell me the syllabus topics separated by commas, Sir.")
        syllabus = listen(phrase_time_limit=30)
        speak("What is the exam date? Please say it in YYYY-MM-DD format, Sir.")
        exam_date = listen(timeout=10)
        if syllabus and exam_date:
            result = self.create_study_timetable(syllabus, exam_date.strip())
            print(result)
            speak(
                f"Timetable created for your exam on {exam_date.strip()}, Sir. "
                "I have displayed the full schedule on screen."
            )
        else:
            speak("Could not create timetable. Please try again, Sir.")
        return True

    def _handle_mcq(self, command: str, **_) -> bool:
        speak("What topic should I create questions for, Sir?")
        topic = listen(phrase_time_limit=10)
        if topic:
            speak(f"Generating MCQ questions on {topic}, Sir. One moment.")
            result = self._brain.generate_mcq(topic)
            print(result)
            speak("Done, Sir. The questions are displayed on your screen.")
        return True

    def _handle_todo(self, command: str, **_) -> bool:
        speak("Please list your tasks separated by commas, Sir.")
        raw = listen(phrase_time_limit=30)
        if raw:
            tasks = [t.strip() for t in raw.split(",") if t.strip()]
            self.create_todo_list(tasks)
        return True

    def _handle_time(self, command: str, **_) -> bool:
        now_str = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"It is {now_str}, Sir.")
        return True

    def _handle_date(self, command: str, **_) -> bool:
        date_str = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today is {date_str}, Sir.")
        return True

    def _handle_remember(self, command: str, **_) -> bool:
        info = (
            command.replace("remember", "")
            .replace("please", "")
            .replace("stark", "")
            .strip()
        )
        if info:
            self.remember(info)
        else:
            speak("What would you like me to remember, Sir?")
        return True

    def _handle_recall(self, command: str, **_) -> bool:
        speak(self.memory.summary())
        return True

    def _handle_role_change(self, command: str, **_) -> bool:
        role = (
            command.replace("act as", "")
            .replace("switch to", "")
            .replace("stark", "")
            .strip()
        )
        if role:
            self.current_role = role
            speak(f"Understood, Sir. I am now acting as your {role}. How can I help?")
        return True

    def _handle_reminder(self, command: str, **_) -> bool:
        speak("What should I remind you about, Sir?")
        reminder_text = listen(phrase_time_limit=15)
        speak("At what time, Sir?")
        reminder_time = listen(timeout=10)
        speak(f"Reminder set: {reminder_text!r} at {reminder_time}, Sir.")
        return True

    def _handle_plan(self, command: str, **_) -> bool:
        """Decompose a high-level goal into an ordered plan using the Planner."""
        import re
        # Remove trigger phrases (longest first to avoid partial overlap)
        # then strip filler words from the goal string.
        goal = re.sub(
            r"\b(stark|create plan for|make plan for|help me plan|plan my|create plan|make plan|plan)\b",
            "",
            command,
            flags=re.IGNORECASE,
        ).strip()
        if not goal:
            speak("What goal would you like me to plan, Sir?")
            goal = listen(phrase_time_limit=20)
        if goal:
            plan_text = self._planner.plan_as_text(goal)
            print(plan_text)
            speak(
                f"I have created a plan for '{goal}', Sir. "
                "The steps are displayed on your screen."
            )
        return True

    # ------------------------------------------------------------------
    # Capability implementations
    # ------------------------------------------------------------------

    def open_youtube(self, query: str) -> None:
        speak(f"Opening YouTube for {query}, Sir.")
        try:
            import pywhatkit as pwk  # type: ignore

            pwk.playonyt(query)
        except ImportError:
            webbrowser.open(
                f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            )

    def open_website(self, url: str) -> None:
        if not url.startswith("http"):
            url = "https://" + url
        speak(f"Opening {url}, Sir.")
        webbrowser.open(url)

    def send_whatsapp_message(
        self, phone_number: str, message: str,
        hour: int = None, minute: int = None,
    ) -> str:
        try:
            import pywhatkit as pwk  # type: ignore

            now = datetime.datetime.now()
            scheduled = now + datetime.timedelta(minutes=2)
            h = hour if hour is not None else scheduled.hour
            m = minute if minute is not None else scheduled.minute
            pwk.sendwhatmsg(phone_number, message, h, m)
            return f"WhatsApp message scheduled to {phone_number}, Sir."
        except ImportError:
            return "pywhatkit is not installed, Sir. Run: pip install pywhatkit"
        except Exception as exc:  # noqa: BLE001
            return f"Failed to send WhatsApp message, Sir: {exc}"

    def access_camera(self) -> None:
        try:
            import cv2  # type: ignore

            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                speak("Camera is not available, Sir.")
                return
            speak("Camera active, Sir. Press Q to close.")
            while True:
                ret, frame = cap.read()
                if ret:
                    cv2.imshow("STARK Vision", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
            cap.release()
            cv2.destroyAllWindows()
        except ImportError:
            speak("OpenCV is not installed, Sir. Run: pip install opencv-python")

    def take_photo(self) -> None:
        try:
            import cv2  # type: ignore

            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"stark_photo_{ts}.jpg"
                    cv2.imwrite(filename, frame)
                    speak(f"Photo saved as {filename}, Sir.")
            else:
                speak("Camera not available, Sir.")
            cap.release()
        except ImportError:
            speak("OpenCV is not installed, Sir.")

    def create_study_timetable(self, syllabus: str, exam_date_str: str) -> str:
        from study_module import StudyModule  # type: ignore

        result = StudyModule.create_timetable(syllabus, exam_date_str)
        if isinstance(result, dict):
            self.study_timetable = result["timetable"]
            self.exam_schedule = {
                "exam_date": exam_date_str,
                "syllabus": result["topics"],
            }
            return result["summary"]
        return result

    def create_todo_list(self, tasks: list) -> list:
        todo = [{"id": i, "task": t, "done": False} for i, t in enumerate(tasks, 1)]
        speak(f"To-do list created with {len(tasks)} items, Sir.")
        return todo

    def set_busy(self, busy: bool) -> None:
        self.busy = busy
        if busy:
            speak("Busy mode activated, Sir. I will handle incoming messages.")
        else:
            speak("Busy mode deactivated, Sir.")

    def handle_incoming_call(self, caller: str) -> str:
        if self.busy:
            self.missed_calls[caller] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return self.busy_message
        return ""

    def remember(self, info: str) -> None:
        self.memory.store(info)
        speak(f"I will remember that, Sir: {info}")

    def recall_semantic(self, query: str) -> str:
        """Return the best matching memory for *query*, using semantic search."""
        results = self.memory.recall(query)
        if not results:
            return "I could not find anything matching that, Sir."
        top = results[0]
        return f"I recall: {top['value']}"

    def recall_all(self) -> str:
        """Return a human-readable summary of all stored memories."""
        return self.memory.summary()

    def start_work_session(self) -> None:
        self.work_start_time = datetime.datetime.now()
        speak("Work session started, Sir. I will remind you to take breaks.")

    def check_work_duration(self) -> None:
        if self.work_start_time:
            elapsed = (datetime.datetime.now() - self.work_start_time).seconds // 60
            if elapsed >= 90:
                speak(
                    f"Sir, you have been working for {elapsed} minutes. "
                    "Please take a short break, drink some water, and rest your eyes."
                )

    def remind_exam(self) -> None:
        if not self.exam_schedule.get("exam_date"):
            return
        try:
            exam_date = datetime.datetime.strptime(self.exam_schedule["exam_date"], "%Y-%m-%d")
            days_left = (exam_date - datetime.datetime.now()).days
            if 0 < days_left <= 7:
                speak(
                    f"Sir, your exam is in {days_left} day(s). "
                    "Please focus on preparation. You can do it!"
                )
        except ValueError:
            pass

    # ------------------------------------------------------------------
    # Main command dispatcher
    # ------------------------------------------------------------------

    def process_command(self, command: str) -> bool:
        """
        Dispatch *command* through the intent registry.

        Returns
        -------
        bool
            ``False`` when the assistant should shut down, ``True`` otherwise.
        """
        command = command.lower().strip()
        if not command:
            return True

        self.remind_exam()
        self.check_work_duration()

        result = self._registry.dispatch(command)
        if result is False:
            return False
        if result is None:
            # No intent matched — fall back to the Gemini AI brain
            response = self._brain.ask(command, role=self.current_role)
            speak(response)

        return True
