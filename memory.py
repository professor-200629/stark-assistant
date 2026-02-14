class MemoryManager:
    def __init__(self):
        self.preferences = {}
        self.conversation_history = []
        self.learned_information = {}  
        self.personal_details = {}

    def store_information(self, key, value):
        """Store information based on a key-value pair."""
        self.learned_information[key] = value
        return "Information stored successfully, Sir."

    def retrieve_information(self, key):
        """Retrieve information based on the key provided."""
        return self.learned_information.get(key, "No information found for this key, Sir.")

    def update_information(self, key, value):
        """Update existing information based on a key-value pair."""
        if key in self.learned_information:
            self.learned_information[key] = value
            return "Information updated successfully, Sir."
        else:
            return "No information found for this key to update, Sir."

    def clear_information(self):
        """Clear all stored information."""
        self.learned_information.clear()
        return "All information cleared successfully, Sir."

    def add_to_conversation_history(self, conversation):
        """Add a conversation record to the history."""
        self.conversation_history.append(conversation)
        return "Conversation history updated, Sir."

    def search_memories(self, query):
        """Search through stored memories based on a query."""
        results = {key: value for key, value in self.learned_information.items() if query.lower() in key.lower()}
        if results:
            return results
        else:
            return "No memories found matching the query, Sir."     

    def store_preferences(self, key, value):
        """Store user preferences."""
        self.preferences[key] = value
        return "Preferences stored successfully, Sir."

    def retrieve_preferences(self, key):
        """Retrieve user preferences."""
        return self.preferences.get(key, "No preference found for this key, Sir.")

    def store_personal_details(self, detail, value):
        """Store personal details of the user."""
        self.personal_details[detail] = value
        return "Personal details stored successfully, Sir."

    def retrieve_personal_details(self, detail):
        """Retrieve personal details of the user."""
        return self.personal_details.get(detail, "No personal detail found for this key, Sir.")
