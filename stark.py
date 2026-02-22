"""
STARK - Personal AI Operating System
Voice-first, human-like personal assistant with AI brain, system control,
study tools, communication, entertainment and more.
"""

import os
import datetime
import random
import threading
import webbrowser

import pyttsx3
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# TTS / Voice helpers
# ---------------------------------------------------------------------------

_tts_engine = pyttsx3.init()
_tts_lock = threading.Lock()


def speak(text: str) -> None:
    """Speak *text* aloud and print it to stdout."""
    print(f"STARK: {text}")
    with _tts_lock:
        _tts_engine.say(text)
        _tts_engine.runAndWait()


def listen(timeout: int = 8, phrase_time_limit: int = 12) -> str:
    """Listen for one spoken command and return the recognised text (lowercase)."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening, Sir...")
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        try:
            audio = recognizer.listen(
                source, timeout=timeout, phrase_time_limit=phrase_time_limit
            )
            command = recognizer.recognize_google(audio)
            print(f"Sir said: {command}")
            return command.lower().strip()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            speak("Sorry, Sir, I did not catch that.")
            return ""
        except sr.RequestError:
            speak("Speech service is unavailable, Sir.")
            return ""


# ---------------------------------------------------------------------------
# StarkAssistant
# ---------------------------------------------------------------------------

class StarkAssistant:
    """Central STARK brain that routes commands to the right capability."""

    _KNOWN_SITES = {
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
        self.current_role = "assistant"
        self.memory = {}
        self.conversation_history = []
        self.exam_schedule = {}
        self.study_timetable = {}
        self.busy = False
        self.busy_message = (
            "Balu is busy right now. I am STARK, his personal AI assistant. "
            "If it is urgent, please leave a message and I will inform him. "
            "For emergencies, please say emergency and I will notify him immediately."
        )
        self.missed_calls = {}
        self.work_start_time = None
        self._gemini_model = None
        self._init_gemini()
        self._greet()

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _init_gemini(self) -> None:
        """Configure the Gemini generative model if the API key is present."""
        try:
            import google.generativeai as genai  # type: ignore

            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self._gemini_model = genai.GenerativeModel("gemini-pro")
                print("Gemini AI brain online, Sir.")
            else:
                print("Warning: GEMINI_API_KEY not set - AI brain limited.")
        except ImportError:
            print("Warning: google-generativeai not installed - AI brain disabled.")

    def _greet(self) -> None:
        """Greet the user based on the current time of day."""
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            msg = "Good morning, Sir! STARK is online and ready to serve you."
        elif 12 <= hour < 17:
            msg = "Good afternoon, Sir! How may I assist you today?"
        elif 17 <= hour < 21:
            msg = "Good evening, Sir! STARK at your service."
        else:
            msg = "Hello, Sir. STARK is online. Working late tonight?"
        speak(msg)

    # ------------------------------------------------------------------
    # AI brain
    # ------------------------------------------------------------------

    def ask_ai(self, query: str, role: str = "assistant") -> str:
        """Return an AI-generated response from Gemini."""
        if self._gemini_model is None:
            return (
                "My AI brain is not available, Sir. "
                "Please configure GEMINI_API_KEY in the .env file."
            )
        try:
            system_ctx = (
                "You are STARK, a voice-first personal AI assistant. "
                "Always address the user as Sir. "
                "Be friendly, loyal, calm, proactive, and speak like a human. "
                "Keep answers concise but complete."
            )
            if role and role != "assistant":
                system_ctx += f" You are currently acting as a {role}."

            history_lines = []
            for entry in self.conversation_history[-5:]:
                history_lines.append(f"Sir: {entry['user']}")
                history_lines.append(f"STARK: {entry['stark']}")
            history_text = "\n".join(history_lines)

            prompt = "\n\n".join([system_ctx, history_text, f"Sir: {query}\nSTARK:"])

            response = self._gemini_model.generate_content(prompt)
            answer = response.text

            self.conversation_history.append({"user": query, "stark": answer})
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            return answer
        except Exception as exc:  # noqa: BLE001
            return f"I encountered an error with my AI brain, Sir: {exc}"

    # ------------------------------------------------------------------
    # YouTube / browser
    # ------------------------------------------------------------------

    def open_youtube(self, query: str) -> None:
        """Search and auto-play the top YouTube result for *query*."""
        speak(f"Opening YouTube for {query}, Sir.")
        try:
            import pywhatkit as pwk  # type: ignore

            pwk.playonyt(query)
        except ImportError:
            search = query.replace(" ", "+")
            webbrowser.open(f"https://www.youtube.com/results?search_query={search}")

    def open_website(self, url: str) -> None:
        """Open *url* in the default web browser."""
        if not url.startswith("http"):
            url = "https://" + url
        speak(f"Opening {url}, Sir.")
        webbrowser.open(url)

    # ------------------------------------------------------------------
    # WhatsApp / messaging
    # ------------------------------------------------------------------

    def send_whatsapp_message(
        self, phone_number: str, message: str, hour: int = None, minute: int = None
    ) -> str:
        """Schedule a WhatsApp message via pywhatkit."""
        try:
            import pywhatkit as pwk  # type: ignore

            now = datetime.datetime.now()
            # Add 2 minutes; handle minute overflow into the next hour
            scheduled = now + datetime.timedelta(minutes=2)
            h = hour if hour is not None else scheduled.hour
            m = minute if minute is not None else scheduled.minute
            pwk.sendwhatmsg(phone_number, message, h, m)
            return f"WhatsApp message scheduled to {phone_number}, Sir."
        except ImportError:
            return "pywhatkit is not installed, Sir. Run: pip install pywhatkit"
        except Exception as exc:  # noqa: BLE001
            return f"Failed to send WhatsApp message, Sir: {exc}"

    # ------------------------------------------------------------------
    # System controls
    # ------------------------------------------------------------------

    def control_system(self, action: str) -> None:
        """Delegate OS-level actions to SystemControl."""
        from system_control import SystemControl  # type: ignore

        SystemControl.execute(action, speak_fn=speak)

    # ------------------------------------------------------------------
    # Camera
    # ------------------------------------------------------------------

    def access_camera(self) -> None:
        """Open a live camera feed (press q to close)."""
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
        """Capture a still photo and save it to disk."""
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

    # ------------------------------------------------------------------
    # Study tools
    # ------------------------------------------------------------------

    def create_study_timetable(self, syllabus: str, exam_date_str: str) -> str:
        """Build a day-by-day study timetable up to *exam_date_str*."""
        from study_module import StudyModule  # type: ignore

        result = StudyModule.create_timetable(syllabus, exam_date_str)
        if isinstance(result, dict):
            self.study_timetable = result["timetable"]
            self.exam_schedule = {
                "exam_date": exam_date_str,
                "syllabus": result["topics"],
            }
            return result["summary"]
        return result  # error message string

    def generate_mcq(self, topic: str, num_questions: int = 5) -> str:
        """Use Gemini to generate MCQ questions on *topic*."""
        if self._gemini_model is None:
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
        prompt = "\n".join(lines)
        try:
            return self._gemini_model.generate_content(prompt).text
        except Exception as exc:  # noqa: BLE001
            return f"Error generating MCQs, Sir: {exc}"

    def remind_exam(self) -> None:
        """Proactively remind about an upcoming exam if 7 days or fewer away."""
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

    def create_todo_list(self, tasks: list) -> list:
        """Return a structured to-do list from a plain task list."""
        todo = [{"id": i, "task": t, "done": False} for i, t in enumerate(tasks, 1)]
        speak(f"To-do list created with {len(tasks)} items, Sir.")
        return todo

    # ------------------------------------------------------------------
    # Busy / call handling
    # ------------------------------------------------------------------

    def set_busy(self, busy: bool) -> None:
        """Toggle busy mode."""
        self.busy = busy
        if busy:
            speak("Busy mode activated, Sir. I will handle incoming messages.")
        else:
            speak("Busy mode deactivated, Sir.")

    def handle_incoming_call(self, caller: str) -> str:
        """Return the auto-reply message when the user is marked busy."""
        if self.busy:
            self.missed_calls[caller] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return self.busy_message
        return ""

    # ------------------------------------------------------------------
    # Memory
    # ------------------------------------------------------------------

    def remember(self, info: str) -> None:
        """Store a piece of information in memory."""
        self.memory[info] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        speak(f"I will remember that, Sir: {info}")

    def recall_all(self) -> str:
        """Return a sentence summarising stored memories."""
        if self.memory:
            return "I remember: " + "; ".join(self.memory.keys())
        return "I do not have any stored memories yet, Sir."

    # ------------------------------------------------------------------
    # Work-session health monitor
    # ------------------------------------------------------------------

    def start_work_session(self) -> None:
        """Record the start of a work session for break reminders."""
        self.work_start_time = datetime.datetime.now()
        speak("Work session started, Sir. I will remind you to take breaks.")

    def check_work_duration(self) -> None:
        """Warn if the user has been working for more than 90 minutes."""
        if self.work_start_time:
            elapsed = (datetime.datetime.now() - self.work_start_time).seconds // 60
            if elapsed >= 90:
                speak(
                    f"Sir, you have been working for {elapsed} minutes. "
                    "Please take a short break, drink some water, and rest your eyes."
                )

    # ------------------------------------------------------------------
    # Main command dispatcher
    # ------------------------------------------------------------------

    def process_command(self, command: str) -> bool:
        """
        Parse a natural-language *command* and execute the matching action.
        Returns ``False`` when the assistant should shut down.
        """
        command = command.lower().strip()
        if not command:
            return True

        self.remind_exam()
        self.check_work_duration()

        # Greetings
        if any(w in command for w in ("hello", "hi", "hey stark", "good morning", "good evening")):
            speak(random.choice([
                "Hello, Sir! How may I assist you today?",
                "Hi there, Sir! What can I do for you?",
                "Good to hear from you, Sir! How can I help?",
            ]))

        # YouTube playback
        elif any(w in command for w in ("play ", "youtube", "trailer", " song", "music video")):
            query = command
            for noise in ("stark", "play", "on youtube", "youtube", "in", "trailer",
                          "song", "music video", "please", "open"):
                query = query.replace(noise, "").strip()
            if query:
                self.open_youtube(query)
            else:
                speak("What would you like me to play, Sir?")

        # Open website / app
        elif command.startswith("open "):
            opened = False
            for name, url in self._KNOWN_SITES.items():
                if name in command:
                    self.open_website(url)
                    opened = True
                    break
            if not opened:
                for word in command.split():
                    if "." in word and len(word) > 3:
                        self.open_website(word)
                        opened = True
                        break
            if not opened:
                response = self.ask_ai(command)
                speak(response)

        # WhatsApp messaging
        elif "send" in command and (
            "whatsapp" in command or "message" in command or "text" in command
        ):
            speak("Please say the phone number with country code, Sir.")
            phone = listen(timeout=10)
            speak("What is the message, Sir?")
            msg = listen(phrase_time_limit=20)
            if phone and msg:
                result = self.send_whatsapp_message(phone.replace(" ", ""), msg)
                speak(result)
            else:
                speak("I could not capture all the details, Sir. Please try again.")

        # Busy mode
        elif "busy mode on" in command or "i am busy" in command or "set busy" in command:
            self.set_busy(True)
        elif "busy mode off" in command or "i am free" in command or "not busy" in command:
            self.set_busy(False)

        # System controls
        elif "shutdown" in command or "shut down" in command:
            speak("Are you sure you want to shut down the system, Sir?")
            confirm = listen(timeout=5)
            if confirm and "yes" in confirm:
                self.control_system("shutdown")
            else:
                speak("Shutdown cancelled, Sir.")

        elif "restart" in command or "reboot" in command:
            speak("Are you sure you want to restart, Sir?")
            confirm = listen(timeout=5)
            if confirm and "yes" in confirm:
                self.control_system("restart")
            else:
                speak("Restart cancelled, Sir.")

        elif "lock" in command:
            self.control_system("lock")

        elif "increase volume" in command or "volume up" in command:
            self.control_system("volume_up")
        elif "decrease volume" in command or "volume down" in command or "mute" in command:
            self.control_system("volume_down")

        elif "increase brightness" in command or "brightness up" in command:
            self.control_system("brightness_up")
        elif "decrease brightness" in command or "brightness down" in command:
            self.control_system("brightness_down")

        # Camera
        elif "open camera" in command or "show camera" in command or "camera on" in command:
            self.access_camera()
        elif "take photo" in command or "take picture" in command or "click photo" in command:
            self.take_photo()

        # Study tools
        elif (
            "create timetable" in command
            or "study timetable" in command
            or "exam timetable" in command
        ):
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

        elif "mcq" in command or "multiple choice" in command or "generate questions" in command:
            speak("What topic should I create questions for, Sir?")
            topic = listen(phrase_time_limit=10)
            if topic:
                speak(f"Generating MCQ questions on {topic}, Sir. One moment.")
                result = self.generate_mcq(topic)
                print(result)
                speak("Done, Sir. The questions are displayed on your screen.")

        elif "to do" in command or "todo" in command or "task list" in command:
            speak("Please list your tasks separated by commas, Sir.")
            raw = listen(phrase_time_limit=30)
            if raw:
                tasks = [t.strip() for t in raw.split(",") if t.strip()]
                self.create_todo_list(tasks)

        # Work session health monitor
        elif "start work" in command or "start session" in command:
            self.start_work_session()

        # Time / Date
        elif "time" in command and "timetable" not in command:
            now_str = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"It is {now_str}, Sir.")
        elif "date" in command:
            date_str = datetime.datetime.now().strftime("%B %d, %Y")
            speak(f"Today is {date_str}, Sir.")

        # Memory
        elif "remember" in command:
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
        elif "what do you know" in command or "what do you remember" in command:
            speak(self.recall_all())

        # Role change
        elif "act as" in command or "switch to" in command:
            role = (
                command.replace("act as", "")
                .replace("switch to", "")
                .replace("stark", "")
                .strip()
            )
            self.current_role = role
            speak(f"Understood, Sir. I am now acting as your {role}. How can I help?")

        # Reminders
        elif "remind me" in command or "set reminder" in command:
            speak("What should I remind you about, Sir?")
            reminder_text = listen(phrase_time_limit=15)
            speak("At what time, Sir?")
            reminder_time = listen(timeout=10)
            speak(f"Reminder set: {reminder_text!r} at {reminder_time}, Sir.")

        # Exit
        elif any(w in command for w in ("goodbye", "bye", "exit", "quit", "sleep")):
            speak("Goodbye, Sir. It has been a pleasure serving you. STARK going offline.")
            return False

        # Education / general AI
        elif any(w in command for w in (
            "explain", "what is", "how does", "how to", "teach me",
            "tell me about", "solve", "answer", "define",
        )):
            response = self.ask_ai(command, role=self.current_role or "teacher")
            speak(response)

        # Health
        elif any(w in command for w in ("health", "doctor", "medicine", "sick", "pain", "tired")):
            response = self.ask_ai(command, role="doctor")
            speak(response)

        # Travel
        elif any(w in command for w in ("travel", "hotel", "restaurant", "tourist", "visit")):
            response = self.ask_ai(command, role="travel guide")
            speak(response)

        # Entertainment
        elif any(w in command for w in ("movie", "show", "recommend", "suggest")):
            response = self.ask_ai(command, role="entertainment advisor")
            speak(response)

        # Default AI response
        else:
            response = self.ask_ai(command, role=self.current_role)
            speak(response)

        return True


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Start STARK in interactive voice mode."""
    print("=" * 50)
    print("  STARK - Personal AI Operating System")
    print("=" * 50)

    assistant = StarkAssistant()
    print("\nSTARK is ready. Speak your commands, Sir.")
    print("Say 'goodbye' or 'exit' to quit.\n")

    running = True
    while running:
        try:
            command = listen(timeout=10)
            if command:
                running = assistant.process_command(command)
        except KeyboardInterrupt:
            speak("STARK shutting down. Goodbye, Sir.")
            break


if __name__ == "__main__":
    main()
