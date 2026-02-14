class CommunicationModule:
    def __init__(self):
        self.communication_logs = []

    def send_message(self, recipient, message):
        # Code to send message
        log_entry = f"Sent message to {recipient}: {message}"
        self.communication_logs.append(log_entry)
        return log_entry

    def make_call(self, recipient):
        # Code to make a call
        log_entry = f"Called {recipient}"
        self.communication_logs.append(log_entry)
        return log_entry

    def get_logs(self):
        return self.communication_logs

# Example usage:
# comms = CommunicationModule()
# comms.send_message('Alice', 'Hello!')
# comms.make_call('Bob')
# print(comms.get_logs())