import speech_recognition as sr
import pyttsx3

class VoiceModule:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
            try:
                command = self.recognizer.recognize_google(audio)
                print(f"You said: {command}")
                return command
            except sr.UnknownValueError:
                print("Sorry, I did not understand that.")
                return None
            except sr.RequestError:
                print("Could not request results from Google Speech Recognition service.")
                return None

if __name__ == '__main__':
    voice_module = VoiceModule()
    voice_module.speak("Hello, I am your assistant. How can I help you today?")
    command = voice_module.listen()
    if command:
        voice_module.speak(f"You said: {command}").