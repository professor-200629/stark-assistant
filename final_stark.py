import pyttsx3
import speech_recognition as sr
from openai import OpenAI
import webbrowser
import os
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)

# OpenAI API key configuration
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Function to speak the message
def speak(text):
    print(f"[STARK] {text}")
    engine.say(text)
    engine.runAndWait()

# Function for speech recognition
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[STARK] Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        try:
            audio = recognizer.listen(source, timeout=10)
            command = recognizer.recognize_google(audio)
            print(f"[USER] {command}")
            return command.lower()
        except sr.UnknownValueError:
            print("[ERROR] Sorry, I didn't catch that.")
            return None
        except sr.RequestError as e:
            print(f"[ERROR] Could not request results: {e}")
            return None

# Function to initiate YouTube playback
def play_youtube_video(query):
    search_query = query.replace(" ", "+")
    youtube_url = f"https://www.youtube.com/results?search_query={search_query}"
    webbrowser.open(youtube_url)
    speak(f"Opening YouTube search for {query}")

# Function to send WhatsApp message
def send_whatsapp_message(contact, message):
    whatsapp_url = f'https://wa.me/{contact}?text={message.replace(" ", "%20")}'
    webbrowser.open(whatsapp_url)
    speak(f"Opening WhatsApp to send message to {contact}")

# Function to open websites
def open_website(website):
    if not website.startswith('http'):
        website = f"https://{website}"
    webbrowser.open(website)
    speak(f"Opening {website}")

# Function to control system volume
def control_volume(action):
    if "up" in action or "increase" in action:
        os.system('nircmd.exe changesysvolume 5000')
        speak("Increasing volume")
    elif "down" in action or "decrease" in action:
        os.system('nircmd.exe changesysvolume -5000')
        speak("Decreasing volume")
    elif "mute" in action:
        os.system('nircmd.exe mutesysvolume 1')
        speak("Muting volume")

# Function to control brightness
def control_brightness(action):
    if "up" in action or "increase" in action:
        speak("Increasing brightness")
    elif "down" in action or "decrease" in action:
        speak("Decreasing brightness")

# Function to open settings
def open_settings():
    os.startfile("ms-settings:")
    speak("Opening Windows Settings")

# Function to shutdown
def shutdown_system():
    speak("Shutting down the system in 30 seconds")
    subprocess.call(['shutdown', '/s', '/t', '30'])

# Function to restart
def restart_system():
    speak("Restarting the system in 30 seconds")
    subprocess.call(['shutdown', '/r', '/t', '30'])

# Function to play Spotify songs
def play_spotify(song):
    search_query = song.replace(" ", "+")
    spotify_url = f"https://open.spotify.com/search/{search_query}"
    webbrowser.open(spotify_url)
    speak(f"Opening Spotify to play {song}")

# Function to integrate OpenAI chat with modern API
def chat_with_openai(prompt):
    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"[ERROR] OpenAI error: {e}")
        return "I encountered an error processing your request."

# Main loop to listen for commands
def main():
    speak("Hello Sir. I am STARK, your personal AI assistant. What would you like me to do?")
    
    while True:
        command = listen()
        
        if command is None:
            continue
        
        if command in ['exit', 'quit', 'goodbye', 'bye', 'stop']:
            speak("Goodbye Sir. See you next time.")
            break
        
        # YouTube commands
        if "play" in command and ("youtube" in command or "video" in command):
            video_query = command.replace("play", "").replace("youtube", "").replace("video", "").strip()
            play_youtube_video(video_query)
        
        # WhatsApp commands
        elif "whatsapp" in command or "send message" in command:
            speak("Please provide the phone number and message you want to send.")
        
        # Website commands
        elif "open" in command:
            website = command.replace("open", "").strip()
            open_website(website)
        
        # Settings command
        elif "settings" in command:
            open_settings()
        
        # Volume control
        elif "volume" in command:
            control_volume(command)
        
        # Brightness control
        elif "brightness" in command or "bright" in command:
            control_brightness(command)
        
        # Shutdown command
        elif "shutdown" in command or "shut down" in command:
            shutdown_system()
        
        # Restart command
        elif "restart" in command or "reboot" in command:
            restart_system()
        
        # Spotify command
        elif ("play" in command and "spotify" in command) or ("play" in command and ("song" in command or "music" in command)):
            song = command.replace("play", "").replace("spotify", "").replace("song", "").replace("music", "").strip()
            play_spotify(song)
        
        # General AI chat
        else:
            response = chat_with_openai(command)
            speak(response)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n[STARK] Shutting down...")
    except Exception as e:
        print(f"[FATAL ERROR] {e}")