# Memory Module for Long-Term Storage and Learning

import datetime

class MemoryModule:
    def __init__(self):
        self.storage = {}

    def save_memory(self, key, value):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.storage[key] = {'value': value, 'timestamp': timestamp}
        print(f'Memory saved: {key} => {value} at {timestamp}')

    def retrieve_memory(self, key):
        if key in self.storage:
            return self.storage[key]
        else:
            print(f'Memory for key {key} not found.')
            return None

    def get_all_memories(self):
        return self.storage

# Example usage:
# memory = MemoryModule()
# memory.save_memory('favorite_color', 'blue')
# print(memory.retrieve_memory('favorite_color'))
