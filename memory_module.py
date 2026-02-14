# memory_module.py

class MemoryModule:
    def __init__(self):
        self.memories = {}

    def store_memory(self, user_id, memory):
        if user_id not in self.memories:
            self.memories[user_id] = []
        self.memories[user_id].append(memory)

    def retrieve_memories(self, user_id):
        return self.memories.get(user_id, [])

    def update_profile(self, user_id, profile_info):
        if user_id not in self.memories:
            self.memories[user_id] = []
        self.memories[user_id].append(profile_info)
    
# Example usage:
# memory_module = MemoryModule()
# memory_module.store_memory('user_123', 'User visited the homepage.')