import pyttsx3
import speech_recognition as sr
import random

# Initialize Text-to-Speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# Initialize speech recognition
recognizer = sr.Recognizer()  

# Function to listen for user input
def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        command = ""
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
        except sr.RequestError:
            speak("Sorry, my speech service is down.")
        return command

# Function to handle responses based on user command
def respond_to_command(command):
    # Define personality modes
    cheerful_responses = ["Sure! Let's have some fun!", "I'm excited to help!", "Yay! Let's go!"]
    thoughtful_responses = ["Hmm, that's an interesting thought.", "Let's ponder that a bit more.", "I think we should explore this further."]
    humorous_responses = ["Why don’t scientists trust atoms? Because they make up everything!", "I told my computer I needed a break, and now it won’t stop sending me KitKat ads.", "Let’s have some fun with this!"]
    professional_responses = ["Of course, I am here to assist you professionally.", "Let's adhere to the guidelines.", "Your request is important, let’s proceed efficiently."]
    
    # Handling greetings
    if "hello" in command or "hi" in command:
        speak(random.choice(cheerful_responses))
    # Handling personality changes
    elif "cheerful" in command:
        speak("Switching to a cheerful mode!")
    elif "thoughtful" in command:
        speak("Switching to a thoughtful mode!")
    elif "humorous" in command:
        speak("Switching to a humorous mode!")
    elif "professional" in command:
        speak("Switching to a professional mode!")
    # Movie suggestions
    elif "movie" in command:
        speak("I suggest you watch Inception or The Matrix.")
    # Story creation
    elif "story" in command:
        speak("Once upon a time in a land far away...")
    # Teaching mode
    elif "teach" in command:
        speak("What would you like to learn today?")
    # Health advice
    elif "health" in command:
        speak("Make sure to stay hydrated and exercise regularly.")
    # Entertainment
    elif "entertainment" in command:
        speak("How about a movie or a new book?")
    # Shopping
    elif "shopping" in command:
        speak("What do you want to buy today?")
    # Travel guidance
    elif "travel" in command:
        speak("Where would you like to travel to?")
    # Task automation
    elif "tasks" in command:
        speak("What task would you like me to automate?")
    # Security checks
    elif "security" in command:
        speak("Please input your security questions or codes.")
    # Engaging dialogue
    elif command:
        speak("That's interesting! Tell me more.")
    else:
        speak("I'm here to assist with anything you need!")

# Main function to start interaction
if __name__ == "__main__":
    while True:
        command = listen()
        respond_to_command(command)