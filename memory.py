import json
from datetime import datetime

class Memory:
    def __init__(self):
        self.long_term_memory = {}
        self.short_term_memory = []
        self.preferences = {}
        self.learning_history = []

    def store_long_term_memory(self, key, value):
        memory_entry = {'key': key, 'value': value, 'timestamp': datetime.now().isoformat()}
        self.long_term_memory[key] = memory_entry
        return f"Memory stored: {key}, Sir."

    def store_short_term_memory(self, content):
        memory_entry = {'content': content, 'timestamp': datetime.now().isoformat()}
        self.short_term_memory.append(memory_entry)
        return f"Short-term memory recorded, Sir."

    def recall_memory(self, key):
        if key in self.long_term_memory:
            return self.long_term_memory[key]['value']
        return f"Memory '{key}' not found, Sir."

    def store_preference(self, preference_name, preference_value):
        self.preferences[preference_name] = preference_value
        return f"Preference '{preference_name}' updated to '{preference_value}', Sir."

    def get_preference(self, preference_name):
        if preference_name in self.preferences:
            return self.preferences[preference_name]
        return f"Preference '{preference_name}' not found, Sir."