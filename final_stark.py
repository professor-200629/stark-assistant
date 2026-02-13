import pyttsx3
import sys
from time import sleep

class StarkAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.voice = self.engine.getProperty('voices')[0]
        self.engine.setProperty('voice', self.voice.id)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen_for_commands(self):
        while True:
            command = input('Enter command: ')
            if command == 'exit':
                self.speak('Exiting. Goodbye!')
                break
            self.process_command(command)

    def process_command(self, command):
        if 'YouTube' in command:
            self.speak('Playing YouTube')
            # Add YouTube functionality
        elif 'WhatsApp' in command:
            self.speak('Opening WhatsApp')
            # Add WhatsApp functionality
        elif 'Spotify' in command:
            self.speak('Playing on Spotify')
            # Add Spotify functionality
        elif 'OpenAI' in command:
            self.speak('Starting OpenAI chat')
            # Add OpenAI chat functionality
        elif 'system' in command:
            self.speak('Executing system command')
            # Add system control functionality
        else:
            self.speak('Command not recognized')

if __name__ == '__main__':
    assistant = StarkAssistant()
    assistant.listen_for_commands()