"""
system_control.py – OS-level controls for STARK.

Supports: shutdown, restart, lock, volume_up/down, brightness_up/down.
Works on Windows, macOS, and Linux with graceful fallbacks.
"""

import os
import platform
import subprocess


class SystemControl:
    """Static helper that maps action names to OS commands."""

    @staticmethod
    def execute(action: str, speak_fn=None) -> None:
        """
        Execute an OS-level *action*.

        Parameters
        ----------
        action:
            One of: shutdown, restart, lock, volume_up, volume_down,
            brightness_up, brightness_down.
        speak_fn:
            Optional callable used to voice feedback.  Defaults to ``print``.
        """
        say = speak_fn if callable(speak_fn) else print
        system = platform.system().lower()

        if action == "shutdown":
            say("Shutting down the system, Sir. Goodbye!")
            SystemControl._run_os(
                windows="shutdown /s /t 1",
                linux="shutdown -h now",
                mac="osascript -e 'tell app \"System Events\" to shut down'",
            )

        elif action == "restart":
            say("Restarting the system, Sir.")
            SystemControl._run_os(
                windows="shutdown /r /t 1",
                linux="reboot",
                mac="osascript -e 'tell app \"System Events\" to restart'",
            )

        elif action == "lock":
            say("Locking the screen, Sir.")
            SystemControl._run_os(
                windows="rundll32.exe user32.dll,LockWorkStation",
                linux="xdg-screensaver lock",
                mac='osascript -e \'tell app "System Events" to keystroke "q" '
                    'using {control down, command down}\'',
            )

        elif action == "volume_up":
            say("Increasing volume, Sir.")
            SystemControl._change_volume(+10, system)

        elif action == "volume_down":
            say("Decreasing volume, Sir.")
            SystemControl._change_volume(-10, system)

        elif action == "brightness_up":
            say("Increasing brightness, Sir.")
            SystemControl._change_brightness(+10, system)

        elif action == "brightness_down":
            say("Decreasing brightness, Sir.")
            SystemControl._change_brightness(-10, system)

        else:
            say(f"Unknown system action: {action}, Sir.")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _run_os(windows: str = "", linux: str = "", mac: str = "") -> None:
        """Pick the correct shell command for the current OS and run it."""
        system = platform.system().lower()
        cmd = ""
        if system == "windows":
            cmd = windows
        elif system == "darwin":
            cmd = mac
        else:
            cmd = linux
        if cmd:
            os.system(cmd)

    @staticmethod
    def _change_volume(delta: int, system: str) -> None:
        """Adjust system volume by *delta* percent."""
        try:
            import pyautogui  # type: ignore

            key = "volumeup" if delta > 0 else "volumedown"
            for _ in range(abs(delta) // 5):
                pyautogui.press(key)
        except ImportError:
            if system == "linux":
                direction = "+" if delta > 0 else "-"
                os.system(f"amixer set Master {abs(delta)}%{direction}")
            elif system == "darwin":
                # macOS: use osascript
                script = (
                    f'tell app "System Events" to set volume output volume '
                    f'(output volume of (get volume settings) + {delta})'
                )
                subprocess.call(["osascript", "-e", script])

    @staticmethod
    def _change_brightness(delta: int, system: str) -> None:
        """Adjust screen brightness by *delta* percent."""
        try:
            import screen_brightness_control as sbc  # type: ignore

            current = sbc.get_brightness(display=0)
            if isinstance(current, list):
                current = current[0]
            new_level = max(10, min(100, current + delta))
            sbc.set_brightness(new_level)
        except ImportError:
            if system == "linux":
                # Fallback: detect first connected display via xrandr
                value = "1.0" if delta > 0 else "0.7"
                os.system(
                    f"xrandr --output $(xrandr | grep ' connected' | "
                    f"head -1 | cut -d' ' -f1) --brightness {value}"
                )
            elif system == "darwin":
                # macOS brightness via osascript is limited; inform the user
                print("Install screen-brightness-control for brightness control, Sir.")
