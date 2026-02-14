import json
from datetime import datetime

class Memory:
    def __init__(self):
        self.long_term_memory = {}
        self.short_term_memory = []
        self.preferences = {}
        self.learning_history = []

    def store_long_term_memory(self, key, value):
        """Store long-term memory about user"""
        memory_entry = {
            'key': key,
            'value': value,
            'timestamp': datetime.now().isoformat()
        }
        self.long_term_memory[key] = memory_entry
        return f"Memory stored: {key}, Sir."

    def store_short_term_memory(self, content):
        """Store short-term memory (conversation context)"""
        memory_entry = {
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        self.short_term_memory.append(memory_entry)
        return f"Short-term memory recorded, Sir."

    def recall_memory(self, key):
        """Recall a specific memory"""
        if key in self.long_term_memory:
            return self.long_term_memory[key]['value']
        return f"Memory '{key}' not found, Sir."

    def store_preference(self, preference_name, preference_value):
        """Store user preferences"""
        self.preferences[preference_name] = preference_value
        return f"Preference '{preference_name}' updated to '{preference_value}', Sir."

    def get_preference(self, preference_name):
        """Retrieve user preference"""
        if preference_name in self.preferences:
            return self.preferences[preference_name]
        return f"Preference '{preference_name}' not found, Sir."

    def record_learning(self, topic, learning_data):
        """Record learning from user interactions"""
        learning_entry = {
            'topic': topic,
            'data': learning_data,
            'timestamp': datetime.now().isoformat()
        }
        self.learning_history.append(learning_entry)
        return f"Learning recorded for {topic}, Sir."

    def get_all_memories(self):
        """Get all stored memories"""
        return {
            'long_term': self.long_term_memory,
            'short_term': self.short_term_memory,
            'preferences': self.preferences,
            'learning_history': self.learning_history
        }

    def clear_short_term_memory(self):
        """Clear short-term memory to free up space"""
        self.short_term_memory = []
        return "Short-term memory cleared, Sir."

    def forget_memory(self, key):
        """Forget a specific memory when asked"""
        if key in self.long_term_memory:
            del self.long_term_memory[key]
            return f"Memory '{key}' forgotten as requested, Sir."
        return f"Memory '{key}' not found, Sir."

if __name__ == '__main__':
    memory = Memory()
    print(memory.store_long_term_memory('favorite_color', 'blue'))
    print(memory.store_preference('language', 'English'))
    print(memory.recall_memory('favorite_color'))
    print(memory.get_preference('language'))