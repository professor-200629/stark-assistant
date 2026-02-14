import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class CommunicationModule:
    def __init__(self):
        self.outgoing_messages = []
        self.incoming_messages = []
        self.call_logs = []

    def send_message(self, recipient, message, platform='sms'):
        """Send a message to recipient via specified platform"""
        msg_obj = {
            'id': len(self.outgoing_messages) + 1,
            'recipient': recipient,
            'message': message,
            'platform': platform,
            'sent_at': datetime.now(),
            'status': 'sent'
        }
        self.outgoing_messages.append(msg_obj)
        return f"Message sent to {recipient} via {platform}, Sir."

    def send_email(self, recipient, subject, body):
        """Send an email"""
        msg_obj = {
            'id': len(self.outgoing_messages) + 1,
            'recipient': recipient,
            'subject': subject,
            'body': body,
            'platform': 'email',
            'sent_at': datetime.now(),
            'status': 'sent'
        }
        self.outgoing_messages.append(msg_obj)
        return f"Email sent to {recipient} with subject '{subject}', Sir."

    def receive_message(self, sender, message, platform='sms'):
        """Receive a message from sender"""
        msg_obj = {
            'id': len(self.incoming_messages) + 1,
            'sender': sender,
            'message': message,
            'platform': platform,
            'received_at': datetime.now()
        }
        self.incoming_messages.append(msg_obj)
        return f"Message received from {sender}, Sir."

    def make_call(self, contact_number):
        """Initiate a call to contact"""
        call_obj = {
            'id': len(self.call_logs) + 1,
            'contact': contact_number,
            'type': 'outgoing',
            'started_at': datetime.now(),
            'status': 'initiated'
        }
        self.call_logs.append(call_obj)
        return f"Calling {contact_number}, Sir."

    def answer_call(self, caller_id):
        """Answer an incoming call"""
        call_obj = {
            'id': len(self.call_logs) + 1,
            'contact': caller_id,
            'type': 'incoming',
            'answered_at': datetime.now(),
            'status': 'active'
        }
        self.call_logs.append(call_obj)
        return f"Call answered from {caller_id}, Sir."

    def auto_respond_to_call(self, caller_id, is_emergency=False):
        """Auto respond to calls when user is busy"""
        if is_emergency:
            response = f"Sir is currently unavailable. This is an emergency, so I will notify him immediately."
            return response
        else:
            response = f"Sir is currently busy. I am STARK, his personal AI assistant. I will inform him of your call. If it's urgent, please leave a message."
            return response

    def send_status_message(self, recipient, status_msg):
        """Send status update to caller"""
        msg_obj = {
            'id': len(self.outgoing_messages) + 1,
            'recipient': recipient,
            'message': status_msg,
            'platform': 'sms',
            'sent_at': datetime.now(),
            'status': 'sent'
        }
        self.outgoing_messages.append(msg_obj)
        return f"Status message sent to {recipient}, Sir."

    def get_call_logs(self):
        """Get all call logs"""
        return self.call_logs

    def get_message_history(self):
        """Get message history"""
        return {
            'incoming': self.incoming_messages,
            'outgoing': self.outgoing_messages
        }

if __name__ == "__main__":
    comm = CommunicationModule()
    print(comm.send_message("9876543210", "Hello!", "sms"))
    print(comm.send_email("user@example.com", "Test", "This is a test email"))
    print(comm.make_call("9876543210"))
    print(comm.auto_respond_to_call("9876543210"))
