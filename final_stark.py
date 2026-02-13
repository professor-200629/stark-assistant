import pyttsx3
import speech_recognition as sr
import openai
import webbrowser
import os
import subprocess

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# OpenAI API key configuration
openai.api_key = 'YOUR_OPENAI_API_KEY'

# Function to speak the message
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function for speech recognition
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that.")
        return None
    except sr.RequestError:
        print("Could not request results from Google Speech Recognition service.")
        return None

# Function to initiate YouTube playback
def play_youtube_video(url):
    webbrowser.open(url)

# Function to send WhatsApp message (for example via a web browser)
def send_whatsapp_message(contact, message):
    webbrowser.open(f'https://wa.me/{contact}?text={message}')  # contact should be the phone number in international format

# Function to control Spotify (placeholder for actual implementation)
def control_spotify(command):
    print(f"Controlling Spotify with command: {command}")  # Implement Spotify control API integration here

# Function to control system (volume, shutdown, restart)
def system_control(command):
    if command == "shutdown":
        subprocess.call(['shutdown', '/s'])
    elif command == "restart":
        subprocess.call(['shutdown', '/r'])
    else:
        print("Unknown system control command.")

# Function to integrate OpenAI chat
def chat_with_openai(prompt):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': prompt}]
    )
    return response.choices[0].message.content

# Main loop to listen for commands
if __name__ == '__main__':
    speak("Hello! I am your STARK AI assistant.")
    while True:
        command = listen()
        if command:
            if "youtube" in command:
                play_youtube_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # Example video
            elif "whatsapp" in command:
                send_whatsapp_message("+1234567890", "Hello from STARK AI!")  # Example contact
            elif "play" in command:
                control_spotify(command)
            elif "shutdown" in command:
                system_control("shutdown")
            elif "restart" in command:
                system_control("restart")
            elif "chat" in command:
                response = chat_with_openai(command)
                speak(response)