import pyttsx3
import speech_recognition as sr
import random

from communication_module import CommunicationManager
from education_module import EducationModule
from system_control import SystemControl

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

# Module instances
_comm = CommunicationManager()
_edu = EducationModule()
_sys = SystemControl()

# Active language for TTS (BCP-47 language code, e.g. 'en', 'te', 'hi')
_current_language = "en"

# Map of spoken language names to BCP-47 codes (50 languages)
LANGUAGE_MAP = {
    "english": "en", "telugu": "te", "hindi": "hi", "tamil": "ta",
    "kannada": "kn", "malayalam": "ml", "marathi": "mr", "bengali": "bn",
    "gujarati": "gu", "punjabi": "pa", "odia": "or", "urdu": "ur",
    "french": "fr", "german": "de", "spanish": "es", "italian": "it",
    "portuguese": "pt", "russian": "ru", "japanese": "ja", "chinese": "zh",
    "korean": "ko", "arabic": "ar", "turkish": "tr", "dutch": "nl",
    "polish": "pl", "swedish": "sv", "norwegian": "no", "danish": "da",
    "finnish": "fi", "greek": "el", "czech": "cs", "hungarian": "hu",
    "romanian": "ro", "ukrainian": "uk", "thai": "th", "vietnamese": "vi",
    "indonesian": "id", "malay": "ms", "filipino": "tl", "swahili": "sw",
    "hebrew": "he", "persian": "fa", "nepali": "ne", "sinhala": "si",
    "burmese": "my", "khmer": "km", "lao": "lo", "mongolian": "mn",
    "kazakh": "kk", "uzbek": "uz",
}


def set_language(language_name):
    """Switch the TTS language; returns a confirmation string."""
    global _current_language
    lang_code = LANGUAGE_MAP.get(language_name.lower())
    if lang_code:
        _current_language = lang_code
        return f"Language switched to {language_name.capitalize()}, Sir."
    return f"Language '{language_name}' is not supported, Sir."


def speak(text):
    """Speak *text* using the currently active language voice (if available)."""
    voices = engine.getProperty('voices')
    selected = None
    for voice in voices:
        voice_id = voice.id.lower()
        voice_langs = voice.languages or []
        # Check exact token match to avoid 'en' matching 'french', etc.
        id_tokens = voice_id.replace('-', '_').replace('.', '_').split('_')
        if _current_language in voice_langs or _current_language in id_tokens:
            selected = voice
            break
    if selected:
        engine.setProperty('voice', selected.id)
    engine.say(text)
    engine.runAndWait()


# Initialize speech recognition
recognizer = sr.Recognizer()


def listen():
    """Listen for a voice command and return its text."""
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        command = ""
        try:
            command = recognizer.recognize_google(audio, language=_current_language)
            print(f"You said: {command}")
        except sr.UnknownValueError:
            speak("Sorry, Sir, I did not understand that.")
        except sr.RequestError:
            speak("Sorry, Sir, my speech service is down.")
        return command


def respond_to_command(command):
    """Route a voice command to the appropriate handler and speak the response."""
    command_lower = command.lower()

    # ------------------------------------------------------------------
    # Greetings
    # ------------------------------------------------------------------
    if "hello" in command_lower or "hi" in command_lower:
        cheerful = [
            "Good day, Sir! How can I assist you?",
            "Hello, Sir! Always at your service.",
            "Hi Sir! What can I do for you today?",
        ]
        speak(random.choice(cheerful))

    # ------------------------------------------------------------------
    # Busy auto-reply
    # ------------------------------------------------------------------
    elif "busy message" in command_lower or "i am busy" in command_lower:
        speak(_comm.get_busy_message())

    # ------------------------------------------------------------------
    # WhatsApp
    # ------------------------------------------------------------------
    elif "whatsapp" in command_lower and "send" in command_lower:
        speak("Please provide the phone number in international format, Sir.")

    # ------------------------------------------------------------------
    # Language switching  (e.g. "speak in Telugu")
    # ------------------------------------------------------------------
    elif "speak" in command_lower and " in " in command_lower:
        words = command_lower.split()
        try:
            lang = words[words.index("in") + 1]
            speak(set_language(lang))
        except (ValueError, IndexError):
            speak("Please specify a language, Sir.")

    # ------------------------------------------------------------------
    # Education – MCQ generation
    # ------------------------------------------------------------------
    elif "mcq" in command_lower or "multiple choice" in command_lower:
        speak(
            "Generating multiple choice questions for you, Sir. "
            "Please tell me the topic."
        )

    # ------------------------------------------------------------------
    # Education – exam timetable
    # ------------------------------------------------------------------
    elif "timetable" in command_lower or "study plan" in command_lower:
        timetable = _edu.create_exam_timetable()
        if isinstance(timetable, str):
            speak(timetable)
        else:
            speak(f"Exam timetable created with {len(timetable)} study days, Sir.")

    # ------------------------------------------------------------------
    # Education – exam reminders
    # ------------------------------------------------------------------
    elif "exam reminder" in command_lower or "upcoming exam" in command_lower:
        reminders = _edu.get_exam_reminders()
        if reminders:
            for r in reminders:
                speak(
                    f"Sir, you have {r['subject']} exam on {r['exam_date']}, "
                    f"{r['days_left']} days remaining. "
                    f"Topics left: {', '.join(r['topics_remaining'][:3])}."
                )
        else:
            speak("No upcoming exams found in the next 30 days, Sir.")

    # ------------------------------------------------------------------
    # Education – to-do list
    # ------------------------------------------------------------------
    elif "to do" in command_lower or "todo" in command_lower:
        todo = _edu.create_todo_list()
        pending = [t['topic'] for t in todo if not t['done']]
        if pending:
            speak(
                f"You have {len(pending)} topics remaining, Sir: "
                f"{', '.join(pending[:5])}."
            )
        else:
            speak("All topics are covered, Sir!")

    # ------------------------------------------------------------------
    # System – volume
    # ------------------------------------------------------------------
    elif "increase volume" in command_lower or "volume up" in command_lower:
        speak(_sys.increase_volume())
    elif "decrease volume" in command_lower or "volume down" in command_lower:
        speak(_sys.decrease_volume())

    # ------------------------------------------------------------------
    # System – brightness
    # ------------------------------------------------------------------
    elif "increase brightness" in command_lower or "brightness up" in command_lower:
        speak(_sys.increase_brightness())
    elif "decrease brightness" in command_lower or "brightness down" in command_lower:
        speak(_sys.decrease_brightness())

    # ------------------------------------------------------------------
    # System – power (confirmation already obtained by the user asking)
    # ------------------------------------------------------------------
    elif "shutdown" in command_lower or "shut down" in command_lower:
        speak("Shutting down as requested, Sir.")
        _sys.shutdown()
    elif "restart" in command_lower or "reboot" in command_lower:
        speak("Restarting the system, Sir.")
        _sys.restart()
    elif "lock" in command_lower:
        speak(_sys.lock())

    # ------------------------------------------------------------------
    # Browser / YouTube
    # ------------------------------------------------------------------
    elif "youtube" in command_lower and ("open" in command_lower or "play" in command_lower):
        # e.g. "play animal trailer in telugu on youtube"
        query = (
            command_lower
            .replace("open youtube", "")
            .replace("play", "")
            .replace("youtube", "")
            .replace("on", "")
            .strip()
        )
        lang = None
        if " in " in query:
            parts = query.split(" in ", 1)
            query, lang = parts[0].strip(), parts[1].strip()
        speak(_sys.play_youtube(query or "trending", lang))
    elif "open" in command_lower:
        words = command_lower.split()
        try:
            idx = words.index("open") + 1
        except ValueError:
            idx = len(words)
        if idx < len(words):
            speak(_sys.open_website(words[idx]))
        else:
            speak("Please specify a website to open, Sir.")

    # ------------------------------------------------------------------
    # Personality modes
    # ------------------------------------------------------------------
    elif "cheerful" in command_lower:
        speak("Switching to cheerful mode, Sir!")
    elif "thoughtful" in command_lower:
        speak("Switching to thoughtful mode, Sir.")
    elif "humorous" in command_lower:
        speak(
            "Here is a joke, Sir: Why don't scientists trust atoms? "
            "Because they make up everything!"
        )
    elif "professional" in command_lower:
        speak("Switching to professional mode. How may I assist you, Sir?")

    # ------------------------------------------------------------------
    # Existing domain handlers
    # ------------------------------------------------------------------
    elif "movie" in command_lower:
        speak("I suggest you watch Inception or The Matrix, Sir.")
    elif "story" in command_lower:
        speak("Once upon a time in a land far away, Sir…")
    elif "teach" in command_lower:
        speak("What would you like to learn today, Sir?")
    elif "health" in command_lower:
        speak("Make sure to stay hydrated and exercise regularly, Sir.")
    elif "entertainment" in command_lower:
        speak("How about a movie or a new book, Sir?")
    elif "shopping" in command_lower:
        speak("What do you want to buy today, Sir?")
    elif "travel" in command_lower:
        speak("Where would you like to travel to, Sir?")
    elif "tasks" in command_lower:
        speak("What task would you like me to handle, Sir?")
    elif "security" in command_lower:
        speak("Security mode activated, Sir. I am monitoring the system.")

    # ------------------------------------------------------------------
    # Fallback
    # ------------------------------------------------------------------
    elif command_lower:
        speak("That's interesting, Sir! Tell me more.")
    else:
        speak("I'm here to assist with anything you need, Sir!")


# Main function to start interaction
if __name__ == "__main__":
    speak("Good day, Sir. STARK is online and ready.")
    while True:
        command = listen()
        respond_to_command(command)
