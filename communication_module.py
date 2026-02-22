"""
communication_module.py – Messaging and communication for STARK.

Supports WhatsApp (via pywhatkit), SMS (via Twilio), and in-app notifications.
"""

import datetime
import os
from typing import Optional


class CommunicationModule:
    """Handles outgoing messages and in-app notifications for STARK."""

    def __init__(self) -> None:
        self._messages: list = []
        self._notifications: list = []

    # ------------------------------------------------------------------
    # WhatsApp
    # ------------------------------------------------------------------

    def send_whatsapp(
        self,
        phone_number: str,
        message: str,
        hour: int = None,
        minute: int = None,
    ) -> str:
        """
        Schedule a WhatsApp message using pywhatkit.

        Parameters
        ----------
        phone_number:
            Recipient number in international format, e.g. ``+919876543210``.
        message:
            Text to send.
        hour / minute:
            Scheduled delivery time (24-h clock).  Defaults to now + 2 min.
        """
        try:
            import pywhatkit as pwk  # type: ignore

            now = datetime.datetime.now()
            h = hour if hour is not None else now.hour
            m = minute if minute is not None else (now.minute + 2) % 60
            pwk.sendwhatmsg(phone_number, message, h, m)
            self._log_message(phone_number, message, channel="whatsapp")
            return f"WhatsApp message scheduled to {phone_number}, Sir."
        except ImportError:
            return "pywhatkit is not installed, Sir. Run: pip install pywhatkit"
        except Exception as exc:  # noqa: BLE001
            return f"Failed to schedule WhatsApp message, Sir: {exc}"

    def send_whatsapp_instantly(self, phone_number: str, message: str) -> str:
        """Send a WhatsApp message without waiting (opens WhatsApp Web)."""
        try:
            import pywhatkit as pwk  # type: ignore

            pwk.sendwhatmsg_instantly(phone_number, message)
            self._log_message(phone_number, message, channel="whatsapp_instant")
            return f"WhatsApp message sent to {phone_number}, Sir."
        except ImportError:
            return "pywhatkit is not installed, Sir."
        except Exception as exc:  # noqa: BLE001
            return f"Failed to send message, Sir: {exc}"

    # ------------------------------------------------------------------
    # SMS via Twilio
    # ------------------------------------------------------------------

    def send_sms(self, to_number: str, message: str) -> str:
        """Send an SMS via the Twilio REST API."""
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_PHONE_NUMBER")

        if not all([account_sid, auth_token, from_number]):
            return (
                "Twilio credentials are not configured, Sir. "
                "Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and "
                "TWILIO_PHONE_NUMBER in your .env file."
            )
        try:
            from twilio.rest import Client  # type: ignore

            client = Client(account_sid, auth_token)
            client.messages.create(body=message, from_=from_number, to=to_number)
            self._log_message(to_number, message, channel="sms")
            return f"SMS sent to {to_number}, Sir."
        except ImportError:
            return "twilio is not installed, Sir. Run: pip install twilio"
        except Exception as exc:  # noqa: BLE001
            return f"Failed to send SMS, Sir: {exc}"

    # ------------------------------------------------------------------
    # In-app messaging
    # ------------------------------------------------------------------

    def send_message(self, recipient: str, message: str, user_id: str = "") -> str:
        """Store an in-app message (no external delivery)."""
        self._log_message(recipient, message, channel="internal", user_id=user_id)
        return f"Message to {recipient} stored, Sir."

    def get_messages(self, user_id: str = "") -> list:
        """Return all messages (optionally filtered by *user_id*)."""
        if user_id:
            return [m for m in self._messages if m.get("user_id") == user_id]
        return list(self._messages)

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------

    def send_notification(
        self, content: str, user_id: str = "", notification_type: str = "notification"
    ) -> str:
        """Queue an in-app notification."""
        entry = {
            "content": content,
            "type": notification_type,
            "user_id": user_id,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        self._notifications.append(entry)
        return f"Notification queued, Sir."

    def get_notifications(self, user_id: str = "") -> list:
        """Return all notifications (optionally filtered by *user_id*)."""
        if user_id:
            return [n for n in self._notifications if n.get("user_id") == user_id]
        return list(self._notifications)

    # ------------------------------------------------------------------
    # Busy auto-reply helper
    # ------------------------------------------------------------------

    @staticmethod
    def busy_auto_reply(caller: str) -> str:
        """Return the standard busy auto-reply message."""
        return (
            f"Balu is busy right now. I am STARK, his personal AI assistant. "
            f"If it is urgent, please leave a message and I will inform him. "
            f"For emergencies, I will notify him immediately."
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _log_message(
        self,
        recipient: str,
        message: str,
        channel: str = "internal",
        user_id: str = "",
    ) -> None:
        self._messages.append(
            {
                "recipient": recipient,
                "message": message,
                "channel": channel,
                "user_id": user_id,
                "timestamp": datetime.datetime.now().isoformat(),
            }
        )
