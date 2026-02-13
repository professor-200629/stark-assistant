import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import subprocess
# Import additional libraries for specific functionalities

engine = pyttsx3.init()
recognizer = sr.Recognizer()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return ""
        except sr.RequestError:
            speak("Could not request results from Google Speech Recognition service.")
            return ""

def execute_command(command):
    if "youtube" in command:
        url = "https://www.youtube.com"
        webbrowser.open(url)
        speak("Opening YouTube")
    elif "whatsapp" in command:
        # Code to send a WhatsApp message
        pass
    elif "spotify" in command:
        # Code to control Spotify
        pass
    elif "volume" in command:
        # Code to control volume
        pass
    elif "brightness" in command:
        # Code to control brightness
        pass
    elif "shutdown" in command:
        speak("Shutting down the system now.")
        subprocess.call(["shutdown", "/s"])
    elif "restart" in command:
        speak("Restarting the system now.")
        subprocess.call(["shutdown", "/r"])
    elif "settings" in command:
        speak("Opening settings.")
        # Open settings code here
    elif "openai chat" in command:
        speak("Starting OpenAI Chat.")
        # OpenAI chat code here
    else:
        speak("Sorry, I didn't catch that.")

if __name__ == "__main__":
    while True:
        command = listen()
        if command:
            execute_command(command)