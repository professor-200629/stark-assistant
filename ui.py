# User Interface Module for Stark Assistant

class UserInterface:
    def __init__(self):
        self.prompt = "Welcome to Stark Assistant!"

    def display_prompt(self):
        print(self.prompt)

    def get_user_input(self):
        return input("Please enter your command: ")

    def show_error(self, message):
        print(f"Error: {message}")

    def display_result(self, result):
        print(f"Result: {result}")
