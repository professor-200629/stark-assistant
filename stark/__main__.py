"""stark package entry point – ``python -m stark``."""

from stark.voice import speak, listen
from stark.core import StarkAssistant


def main() -> None:
    print("=" * 50)
    print("  STARK - Personal AI Operating System")
    print("=" * 50)

    assistant = StarkAssistant()
    print("\nSTARK is ready. Speak your commands, Sir.")
    print("Say 'goodbye' or 'exit' to quit.\n")

    running = True
    while running:
        try:
            command = listen(timeout=10)
            if command:
                running = assistant.process_command(command)
        except KeyboardInterrupt:
            speak("STARK shutting down. Goodbye, Sir.")
            break


if __name__ == "__main__":
    main()
