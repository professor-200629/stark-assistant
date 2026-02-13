import pyttsx3
import openai
import webbrowser
import os
import subprocess

class StarkAssistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.volume = 1.0
        self.brightness = 100

    def speak(self, text):
        self.engine.setProperty('volume', self.volume)
        self.engine.say(text)
        self.engine.runAndWait()

    def chat_with_openai(self, user_input):
        # Call OpenAI API (ensure proper API key setup)
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': user_input}]
        )
        return response['choices'][0]['message']['content']

    def open_youtube(self):
        webbrowser.open('https://www.youtube.com/')

    def send_whatsapp_message(self, number, message):
        webbrowser.open(f'https://api.whatsapp.com/send?phone={number}&text={message}')

    def play_spotify(self, song):
        # Placeholder for Spotify integration
        # You would typically use the Spotify API here
        print(f'Playing {song} on Spotify')

    def control_volume(self, volume_level):
        self.volume = volume_level
        self.speak(f'Volume set to {self.volume * 100}%')

    def control_brightness(self, brightness_level):
        self.brightness = brightness_level
        self.speak(f'Brightness set to {self.brightness}%')

    def shutdown(self):
        os.system('shutdown /s /t 1')

    def restart(self):
        os.system('shutdown /r /t 1')

    def settings(self):
        # Settings handling can be implemented here
        self.speak('Opening settings.')

    def process_command(self, command):
        try:
            if 'open youtube' in command:
                self.open_youtube()
            elif 'send whatsapp message' in command:
                self.send_whatsapp_message('1234567890', 'Hello!')
            elif 'play song' in command:
                self.play_spotify('Your favorite song')
            elif 'volume' in command:
                volume_level = float(command.split('volume ')[1]) / 100
                self.control_volume(volume_level)
            elif 'brightness' in command:
                brightness_level = int(command.split('brightness ')[1])
                self.control_brightness(brightness_level)
            elif 'shutdown' in command:
                self.shutdown()
            elif 'restart' in command:
                self.restart()
            else:
                response = self.chat_with_openai(command)
                self.speak(response)
        except Exception as e:
            self.speak(f'An error occurred: {str(e)}')

if __name__ == '__main__':
    assistant = StarkAssistant()
    while True:
        user_input = input('How can I assist you? ')
        assistant.process_command(user_input)