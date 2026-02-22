"""
stark/voice.py – Speech I/O layer for STARK.

Provides speak() and listen() functions backed by pyttsx3 and
SpeechRecognition.  Both functions print to stdout so they work in
text-only environments where audio hardware is absent.
"""

import threading

import pyttsx3
import speech_recognition as sr

_tts_engine = pyttsx3.init()
_tts_lock = threading.Lock()


def speak(text: str) -> None:
    """Speak *text* aloud and echo it to stdout."""
    print(f"STARK: {text}")
    with _tts_lock:
        _tts_engine.say(text)
        _tts_engine.runAndWait()


def listen(timeout: int = 8, phrase_time_limit: int = 12) -> str:
    """
    Listen for one spoken command.

    Returns
    -------
    str
        Recognised speech in lowercase, or an empty string on failure.
    """
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
