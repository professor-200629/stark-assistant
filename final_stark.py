import os
import sys
import threading
import time
from datetime import datetime
from dotenv import load_dotenv
import speech_recognition as sr
from pyttsx3 import init as pyttsx3_init
from openai import OpenAI
import pyperclip
from PIL import ImageGrab
import base64
import json

# Load environment variables
load_dotenv()

class STARKVoiceModule:
    """Handles voice input and output"""
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3_init()
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
    
    def listen(self, timeout=5):
        """Listen for voice input"""
        try:
            with sr.Microphone() as source:
                print("[STARK] Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = self.recognizer.listen(source, timeout=timeout)
                text = self.recognizer.recognize_google(audio)
                print(f"[USER] {text}")
                return text
        except sr.UnknownValueError:
            self.speak("Sorry Sir, I didn't understand that. Please repeat.")
            return None
        except sr.RequestError:
            self.speak("I'm having trouble connecting to the internet, Sir.")
            return None
        except Exception as e:
            print(f"[ERROR] Listen error: {e}")
            return None
    
    def speak(self, text):
        """Speak text output"""
        try:
            print(f"[STARK] {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[ERROR] Speak error: {e}")

class STARKAIBrain:
    """OpenAI integration for AI responses"""
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        self.client = OpenAI(api_key=api_key)
        self.conversation_history = []
    
    def chat(self, user_message):
        """Get AI response"""
        try:
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=self.conversation_history,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
        except Exception as e:
            print(f"[ERROR] AI error: {e}")
            return "I'm having trouble accessing my AI brain right now, Sir."

class STARKScreenWatcher:
    """Monitor and analyze user screen"""
    def __init__(self, voice_module, ai_brain):
        self.voice_module = voice_module
        self.ai_brain = ai_brain
    
    def capture_screenshot(self):
        """Take screenshot"""
        try:
            screenshot = ImageGrab.grab()
            screenshot.save("temp_screenshot.png")
            return "temp_screenshot.png"
        except Exception as e:
            print(f"[ERROR] Screenshot error: {e}")
            return None
    
    def analyze_screenshot(self, image_path):
        """Analyze screenshot with vision API"""
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            response = self.ai_brain.client.chat.completions.create(
                model="gpt-4-vision",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            },
                            {
                                "type": "text",
                                "text": "What do you see in this screenshot? Describe any errors, code, or important information."
                            }
                        ]
                    }
                ]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"[ERROR] Vision API error: {e}")
            return "I couldn't analyze the screenshot, Sir."

class STARKClipboardMonitor:
    """Monitor clipboard for errors"""
    def __init__(self, voice_module, ai_brain):
        self.voice_module = voice_module
        self.ai_brain = ai_brain
        self.last_clipboard_content = ""
    
    def check_for_errors(self):
        """Check clipboard for error messages"""
        try:
            current_content = pyperclip.paste()
            
            if current_content != self.last_clipboard_content:
                self.last_clipboard_content = current_content
                
                error_keywords = ['Traceback', 'Error:', 'SyntaxError', 'Exception', 'Failed', 'CRITICAL']
                
                if any(keyword in current_content for keyword in error_keywords):
                    self.voice_module.speak("Sir, I detected an error in your code.")
                    print(f"[ERROR DETECTED] {current_content[:200]}")
                    
                    fix_suggestion = self.ai_brain.chat(
                        f"I found this error in my code: {current_content}. What should I do to fix it?"
                    )
                    self.voice_module.speak(f"Sir, I suggest: {fix_suggestion}")
        except Exception as e:
            print(f"[ERROR] Clipboard monitor error: {e}")

class STARKBackgroundWorker(threading.Thread):
    """Background worker for continuous monitoring"""
    def __init__(self, clipboard_monitor):
        super().__init__()
        self.clipboard_monitor = clipboard_monitor
        self.daemon = True
        self.running = True
    
    def run(self):
        """Run background tasks"""
        while self.running:
            self.clipboard_monitor.check_for_errors()
            time.sleep(2)
    
    def stop(self):
        """Stop background worker"""
        self.running = False

class STARK:
    """Main STARK AI Assistant"""
    def __init__(self):
        print("\n" + "="*50)
        print("STARK AI ASSISTANT - INITIALIZING")
        print("="*50 + "\n")
        
        try:
            self.voice = STARKVoiceModule()
            print("[✓] Voice module initialized")
            
            self.brain = STARKAIBrain()
            print("[✓] AI brain initialized")
            
            self.screen_watcher = STARKScreenWatcher(self.voice, self.brain)
            print("[✓] Screen watcher initialized")
            
            self.clipboard_monitor = STARKClipboardMonitor(self.voice, self.brain)
            print("[✓] Clipboard monitor initialized")
            
            self.background_worker = STARKBackgroundWorker(self.clipboard_monitor)
            self.background_worker.start()
            print("[✓] Background worker started")
            
            print("\n" + "="*50)
            print("STARK IS READY!")
            print("="*50 + "\n")
            
            self.greet_user()
        except Exception as e:
            print(f"\n[FATAL ERROR] {e}")
            sys.exit(1)
    
    def greet_user(self):
        """Greet user with current time"""
        hour = datetime.now().hour
        
        if hour < 12:
            greeting = "Good morning Sir"
        elif hour < 18:
            greeting = "Good afternoon Sir"
        else:
            greeting = "Good evening Sir"
        
        full_greeting = f"{greeting}. I'm STARK, your personal AI assistant. I'm ready to help you with anything." 
        self.voice.speak(full_greeting)
    
    def process_command(self, command):
        """Process user commands"""
        command_lower = command.lower()
        
        # Screen watching
        if "look at" in command_lower or "watch screen" in command_lower:
            self.voice.speak("Taking a screenshot, Sir")
            screenshot_path = self.screen_watcher.capture_screenshot()
            if screenshot_path:
                analysis = self.screen_watcher.analyze_screenshot(screenshot_path)
                self.voice.speak(analysis)
        
        # Task management
        elif "remind me" in command_lower:
            self.voice.speak("I'll set a reminder for you, Sir")
            response = self.brain.chat(command)
            self.voice.speak(response)
        
        # General AI chat
        else:
            response = self.brain.chat(command)
            self.voice.speak(response)
    
    def main_loop(self):
        """Main interaction loop"""
        self.voice.speak("You can speak now, Sir. Say 'exit' to stop.")
        
        while True:
            try:
                user_input = self.voice.listen(timeout=10)
                
                if user_input is None:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'goodbye']:
                    self.voice.speak("Goodbye Sir. See you next time.")
                    break
                
                self.process_command(user_input)
                
            except KeyboardInterrupt:
                self.voice.speak("Shutting down, Sir. Goodbye.")
                break
            except Exception as e:
                print(f"[ERROR] Main loop error: {e}")
                self.voice.speak("I encountered an error, Sir. Please try again.")
    
    def shutdown(self):
        """Shutdown STARK gracefully"""
        print("\n[STARK] Shutting down...")
        self.background_worker.stop()
        print("[✓] Background worker stopped")
        print("[✓] STARK shutdown complete")

if __name__ == "__main__":
    try:
        stark = STARK()
        stark.main_loop()
    except KeyboardInterrupt:
        print("\n[STARK] Emergency shutdown")
    except Exception as e:
        print(f"[FATAL] {e}")
    finally:
        if 'stark' in locals():
            stark.shutdown()