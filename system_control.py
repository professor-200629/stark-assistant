# System Control Module

import platform
import subprocess
import webbrowser


class SystemControl:
    """Provides system-level controls: volume, brightness, power, browser, YouTube."""

    def __init__(self):
        self.os_type = platform.system().lower()

    # ------------------------------------------------------------------
    # Power controls (confirmation must be obtained BEFORE calling these)
    # ------------------------------------------------------------------

    def shutdown(self):
        """Shutdown the system."""
        if self.os_type == "windows":
            subprocess.run(["shutdown", "/s", "/t", "0"], check=False)
        else:
            subprocess.run(["shutdown", "-h", "now"], check=False)
        return "Shutting down the system, Sir."

    def restart(self):
        """Restart the system."""
        if self.os_type == "windows":
            subprocess.run(["shutdown", "/r", "/t", "0"], check=False)
        else:
            subprocess.run(["reboot"], check=False)
        return "Restarting the system, Sir."

    def lock(self):
        """Lock the screen."""
        if self.os_type == "windows":
            subprocess.run(
                ["rundll32.exe", "user32.dll,LockWorkStation"], check=False
            )
        elif self.os_type == "darwin":
            subprocess.run(["pmset", "displaysleepnow"], check=False)
        else:
            subprocess.run(["xdg-screensaver", "lock"], check=False)
        return "Screen locked, Sir."

    # ------------------------------------------------------------------
    # Volume controls
    # ------------------------------------------------------------------

    def increase_volume(self, step=10):
        """Increase the system volume by ``step`` percent."""
        if self.os_type == "linux":
            try:
                subprocess.run(
                    ["amixer", "-D", "pulse", "sset", "Master", f"{step}%+"],
                    check=False,
                )
            except FileNotFoundError:
                pass
        elif self.os_type == "windows":
            self._windows_volume_change(step)
        return f"Volume increased by {step}%, Sir."

    def decrease_volume(self, step=10):
        """Decrease the system volume by ``step`` percent."""
        if self.os_type == "linux":
            try:
                subprocess.run(
                    ["amixer", "-D", "pulse", "sset", "Master", f"{step}%-"],
                    check=False,
                )
            except FileNotFoundError:
                pass
        elif self.os_type == "windows":
            self._windows_volume_change(-step)
        return f"Volume decreased by {step}%, Sir."

    def _windows_volume_change(self, delta):
        """Adjust Windows master volume by ``delta`` (positive = increase)."""
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current = volume.GetMasterVolumeLevelScalar()
            new_level = max(0.0, min(1.0, current + delta / 100.0))
            volume.SetMasterVolumeLevelScalar(new_level, None)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Brightness controls
    # ------------------------------------------------------------------

    def increase_brightness(self, step=10):
        """Increase screen brightness by ``step`` percent."""
        return self._adjust_brightness(step)

    def decrease_brightness(self, step=10):
        """Decrease screen brightness by ``step`` percent."""
        return self._adjust_brightness(-step)

    def _adjust_brightness(self, delta):
        try:
            import screen_brightness_control as sbc

            current = sbc.get_brightness(display=0)
            if isinstance(current, list):
                current = current[0]
            new_level = max(0, min(100, current + delta))
            sbc.set_brightness(new_level, display=0)
            direction = "increased" if delta >= 0 else "decreased"
            return f"Brightness {direction}, Sir."
        except ImportError:
            return (
                "screen_brightness_control is not installed. "
                "Run 'pip install screen-brightness-control' to enable this feature, Sir."
            )
        except Exception as exc:
            return f"Could not adjust brightness: {exc}, Sir."

    # ------------------------------------------------------------------
    # Browser / web controls
    # ------------------------------------------------------------------

    def open_website(self, url):
        """Open a URL in the default browser.

        Adds 'https://' if no scheme is present.
        """
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opening {url} in your browser, Sir."

    def play_youtube(self, query, language=None):
        """Search YouTube for *query* (optionally filtering by *language*)."""
        search_query = query.replace(" ", "+")
        if language:
            search_query += "+" + language.replace(" ", "+")
        url = f"https://www.youtube.com/results?search_query={search_query}"
        webbrowser.open(url)
        lang_info = f" in {language}" if language else ""
        return f"Opening YouTube search for '{query}'{lang_info}, Sir."
