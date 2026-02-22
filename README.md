# STARK: Your Personal AI Assistant

## Overview
STARK is a sophisticated personal AI assistant designed to help users manage tasks, communication, and daily activities with ease. With voice capabilities, it enables seamless interaction, making it more accessible and user-friendly.

---

## Getting Started

### Prerequisites

| Requirement | Version |
|---|---|
| Python | 3.9 or higher |
| pip | latest |
| Microphone | required for voice input |
| Speakers / audio output | required for voice output |

> **Windows users:** You may also need to install the
> [Microsoft Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
> before installing `pyaudio`.

---

### 1. Clone the repository

```bash
git clone https://github.com/professor-200629/stark-assistant.git
cd stark-assistant
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Linux users:** If `pyaudio` fails to install, first run:
> ```bash
> sudo apt-get install python3-pyaudio portaudio19-dev
> ```

---

### 3. Set up environment variables

Copy the example environment file and fill in your API keys:

```bash
cp .env.example .env
```

Open `.env` in any text editor and replace the placeholder values:

```
OPENAI_API_KEY=your_openai_api_key_here
TWILIO_API_KEY=your_twilio_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GMAIL_API_KEY=your_gmail_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

> API keys are only needed for optional features (WhatsApp, SMS, email, AI answers).
> STARK's core voice assistant works without any API keys.

---

### 4. Run STARK

#### Voice assistant (recommended — main entry point)

```bash
python stark.py
```

STARK will greet you and start listening for voice commands through your microphone.

#### REST API server

```bash
python api_interface.py
```

The API will be available at `http://127.0.0.1:5000`. Use the endpoints to manage tasks,
messages, and memories programmatically.

#### Desktop UI

```bash
python ui_interface.py
```

Opens the graphical Tkinter dashboard for Tasks, Messages, Memory, and a command console.

---

### 5. Try your first voice commands

Once `stark.py` is running, speak any of the following:

| What you say | What STARK does |
|---|---|
| `"Hello"` | Greets you |
| `"Play Animal trailer in Telugu on YouTube"` | Opens YouTube search |
| `"Open google.com"` | Opens the website in your browser |
| `"Increase volume"` | Raises system volume |
| `"Decrease brightness"` | Lowers screen brightness |
| `"I am busy"` | Reads the busy auto-reply message aloud |
| `"Upcoming exam"` | Lists exams in the next 30 days |
| `"Create timetable"` | Builds a day-by-day study plan |
| `"Generate MCQ"` | Prompts you for a topic then generates questions |
| `"Todo"` | Lists uncovered study topics |
| `"Speak in Telugu"` | Switches STARK's voice to Telugu |
| `"Shutdown"` | Shuts down your computer |

---

### 6. Run the tests

```bash
python test_modules.py
```

---

## Features

### Voice Capabilities
- **Natural Language Processing:** Understands and responds to user queries in natural language.
- **Voice Commands:** Handles tasks through voice commands, allowing hands-free operation.
- **50 Languages:** Switch STARK's speaking language with a single voice command.

### Task Management
- **To-Do Lists:** Create and manage to-do lists; set reminders and deadlines.
- **Calendar Integration:** Sync with calendar applications to help schedule and manage events.

### Communication
- **Messaging:** Send and receive messages through various platforms (SMS, email, etc.).
- **WhatsApp:** Send WhatsApp messages hands-free via voice command.
- **Busy Auto-Reply:** Automatically compose and send a "I'm busy" reply on your behalf.
- **Voice Calls:** Make and receive voice calls directly through the application.

### Education & Exam Prep
- **MCQ Generator:** Generate multiple-choice questions on any topic.
- **Exam Timetable:** Build a personalised day-by-day study plan from your syllabus.
- **Exam Reminders:** Get notified about upcoming exams and remaining topics.
- **To-Do List:** Track which topics you have covered and which remain.

### System Controls
- **Volume & Brightness:** Raise or lower volume and screen brightness by voice.
- **Power Controls:** Shutdown, restart, or lock your computer by voice.
- **Open Websites:** Open any website or YouTube video instantly.

### Health Monitoring
- **Activity Tracking:** Monitor physical activities and provide insights on fitness levels.
- **Health Reminders:** Alert users about medication timings and health check-ups.

### Security
- **Secure Data Handling:** All user data is encrypted and handled securely.
- **Biometric Authentication:** Use fingerprint or facial recognition for enhanced security access.

### Automation
- **Smart Home Integration:** Control smart home devices through voice commands.
- **Routine Automation:** Automate everyday tasks and routines for efficiency.

---

## Conclusion
STARK is not just an assistant; it's a comprehensive tool that enhances productivity, ensures security, and makes daily life easier. Explore its features and elevate your personal and professional life with STARK!