import openai
import pyttsx3
import speech_recognition as sr

class STARK:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.speaker = pyttsx3.init()
        self.openai_api_key = 'your_openai_api_key'
        openai.api_key = self.openai_api_key

    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
            command = self.recognizer.recognize_google(audio)
            return command

    def talk(self, text):
        self.speaker.say(text)
        self.speaker.runAndWait()

    def process_command(self, command):
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': command}]
        )
        answer = response['choices'][0]['message']['content']
        self.talk(answer)

    def run(self):
        while True:
            command = self.listen()
            print(f"Command: {command}")
            self.process_command(command)

if __name__ == '__main__':
    stark = STARK()
    stark.run()