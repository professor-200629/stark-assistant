class STARK:
    def __init__(self):
        self.personalities = ['cheerful', 'thoughtful', 'humorous']
        self.current_personality = 'cheerful'

    def respond(self, command):
        if 'movie suggestion' in command.lower():
            return self.movie_suggestion()
        elif 'tell a story' in command.lower():
            return self.create_story()
        elif 'teach me' in command.lower():
            return self.teach()
        elif 'how are you' in command.lower():
            return self.greet()
        else:
            return "I understand your command, but I'm still learning how to respond. Let's explore together!"

    def movie_suggestion(self):
        return "How about watching 'Inception'? It's a great blend of action and thought-provoking themes!"

    def create_story(self):
        return "Once upon a time, in a digital realm, an AI named STARK..."

    def teach(self):
        return "What would you like to learn today? I can help with many subjects!"

    def greet(self):
        return f"I'm doing great, thanks for asking! How can I assist you today?"

# Example usage:
stark = STARK()
print(stark.respond('Give me a movie suggestion'))