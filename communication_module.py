# Communication Module

from datetime import datetime


class CommunicationManager:
    """Handles messaging, notifications, and busy auto-replies for STARK."""

    BUSY_MESSAGE_TEMPLATE = (
        "{owner} is busy right now. I am STARK, {pronoun} personal AI assistant. "
        "If it is urgent, please let me know and I will inform {pronoun_obj} immediately. "
        "For emergencies, I will notify {pronoun_obj} right away. "
        "Otherwise, {pronoun_obj} will get back to you later. Thank you!"
    )

    def __init__(self, owner_name="balu", pronoun="his", pronoun_obj="him"):
        self.owner_name = owner_name
        self.pronoun = pronoun
        self.pronoun_obj = pronoun_obj
        self.messages = {}
        self.notifications = {}

    def send_message(self, recipient, message, sender_id=None):
        """Send a message to a recipient and store it in the log."""
        if sender_id not in self.messages:
            self.messages[sender_id] = []
        self.messages[sender_id].append({
            'recipient': recipient,
            'message': message,
            'timestamp': datetime.now().isoformat(),
        })
        return f"Message sent to {recipient}, Sir."

    def get_messages(self, user_id):
        """Retrieve all messages for a user."""
        return self.messages.get(user_id, [])

    def send_notification(self, notification, user_id, notification_type="notification"):
        """Store a notification for a user."""
        if user_id not in self.notifications:
            self.notifications[user_id] = []
        self.notifications[user_id].append({
            'message': notification,
            'type': notification_type,
            'timestamp': datetime.now().isoformat(),
        })
        return "Notification sent, Sir."

    def get_notifications(self, user_id):
        """Retrieve all notifications for a user."""
        return self.notifications.get(user_id, [])

    def get_busy_message(self):
        """Return the standard busy auto-reply text."""
        return self.BUSY_MESSAGE_TEMPLATE.format(
            owner=self.owner_name.capitalize(),
            pronoun=self.pronoun,
            pronoun_obj=self.pronoun_obj,
        )

    def send_whatsapp(self, phone_number, message):
        """Send a WhatsApp message via pywhatkit.

        ``phone_number`` must be in international format, e.g. '+919876543210'.
        The message is scheduled 2 minutes from the current time so the
        WhatsApp Web tab has time to open.
        """
        try:
            import pywhatkit
            now = datetime.now()
            pywhatkit.sendwhatmsg(phone_number, message, now.hour, now.minute + 2)
            return f"WhatsApp message sent to {phone_number}, Sir."
        except ImportError:
            return (
                "pywhatkit is not installed. "
                "Run 'pip install pywhatkit' to enable WhatsApp messaging, Sir."
            )
        except Exception as exc:
            return f"Could not send WhatsApp message: {exc}, Sir."

    def send_busy_whatsapp(self, phone_number):
        """Send the busy auto-reply as a WhatsApp message."""
        return self.send_whatsapp(phone_number, self.get_busy_message())