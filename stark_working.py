import speech_recognition as sr  
import pyttsx3  
import webbrowser  
import os  

# Initialize the recognizer and text-to-speech engine  
recognizer = sr.Recognizer()  
tts_engine = pyttsx3.init()  

# Function to speak text  
def speak(text):  
    tts_engine.say(text)  
    tts_engine.runAndWait()  

# Function to listen for commands  
def listen():  
    with sr.Microphone() as source:  
        print("Listening...")  
        audio = recognizer.listen(source)  
        try:  
            command = recognizer.recognize_google(audio).lower()  
            print(f"You said: {command}")  
            return command  
        except sr.UnknownValueError:  
            print("Sorry, I did not hear that.")  
            return None  
        except sr.RequestError:  
            print("Could not request results from Google Speech Recognition service.")  
            return None  

# Main function to run the assistant  
def run_assistant():  
    while True:  
        command = listen()  
        if command:  
            if "youtube" in command:  
                speak("Opening YouTube.")  
                webbrowser.open("https://www.youtube.com")  
            elif "whatsapp" in command:  
                speak("Opening WhatsApp.")  
                webbrowser.open("https://web.whatsapp.com")  
            elif "spotify" in command:  
                speak("Opening Spotify.")  
                os.system("open /Applications/Spotify.app")  
            elif "system control" in command:  
                speak("Controlling system settings.")  
                os.system("open /Applications/System Preferences.app")  
            elif "openai chat" in command:  
                speak("Opening OpenAI Chat.")  
                webbrowser.open("https://chat.openai.com")  
            elif "exit" in command:  
                speak("Goodbye!")  
                break  
            else:  
                speak("I didn't understand that.")  

# Start the assistant  
if __name__ == "__main__":  
    speak("Hello! I am your assistant. How can I help you today?")  
    run_assistant()  
