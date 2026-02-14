import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from main_controller import StarkAssistant
import config

class StarkAssistantUI:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.root.geometry("800x600")
        self.assistant = StarkAssistant(config.DEFAULT_USER_ID)
        self.setup_ui()

    def setup_ui(self):
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(header_frame, text=f"Welcome, Sir. {config.APP_NAME} v{config.APP_VERSION}", font=("Arial", 14, "bold")).pack()

        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tasks Tab
        self.tasks_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_frame, text="Tasks")
        self.setup_tasks_tab()

        # Messages Tab
        self.messages_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.messages_frame, text="Messages")
        self.setup_messages_tab()

        # Memory Tab
        self.memory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.memory_frame, text="Memory")
        self.setup_memory_tab()

        # Console Tab
        self.console_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.console_frame, text="Console")
        self.setup_console_tab()

    def setup_tasks_tab(self):
        # Add Task Section
        add_frame = ttk.LabelFrame(self.tasks_frame, text="Add New Task")
        add_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(add_frame, text="Task Name:").pack(side=tk.LEFT)
        self.task_name_entry = ttk.Entry(add_frame, width=30)
        self.task_name_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(add_frame, text="Add Task", command=self.add_task).pack(side=tk.LEFT, padx=5)

        # Tasks List
        list_frame = ttk.LabelFrame(self.tasks_frame, text="Your Tasks")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tasks_listbox = tk.Listbox(list_frame)
        self.tasks_listbox.pack(fill=tk.BOTH, expand=True)
        ttk.Button(list_frame, text="Refresh", command=self.refresh_tasks).pack(pady=5)

    def setup_messages_tab(self):
        # Send Message Section
        send_frame = ttk.LabelFrame(self.messages_frame, text="Send Message")
        send_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(send_frame, text="Recipient:").pack(side=tk.LEFT)
        self.recipient_entry = ttk.Entry(send_frame, width=20)
        self.recipient_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(send_frame, text="Message:").pack(side=tk.LEFT)
        self.message_entry = ttk.Entry(send_frame, width=40)
        self.message_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(send_frame, text="Send", command=self.send_message).pack(side=tk.LEFT, padx=5)

        # Messages Display
        display_frame = ttk.LabelFrame(self.messages_frame, text="Messages")
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.messages_text = scrolledtext.ScrolledText(display_frame, height=15)
        self.messages_text.pack(fill=tk.BOTH, expand=True)

    def setup_memory_tab(self):
        # Store Memory Section
        store_frame = ttk.LabelFrame(self.memory_frame, text="Store Memory")
        store_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(store_frame, text="Category:").pack(side=tk.LEFT)
        self.memory_category = ttk.Combobox(store_frame, values=config.MEMORY_CATEGORIES, width=15)
        self.memory_category.pack(side=tk.LEFT, padx=5)
        ttk.Label(store_frame, text="Data:").pack(side=tk.LEFT)
        self.memory_data_entry = ttk.Entry(store_frame, width=40)
        self.memory_data_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(store_frame, text="Store", command=self.store_memory).pack(side=tk.LEFT, padx=5)

        # Memory Display
        display_frame = ttk.LabelFrame(self.memory_frame, text="Stored Memories")
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.memory_text = scrolledtext.ScrolledText(display_frame, height=15)
        self.memory_text.pack(fill=tk.BOTH, expand=True)

    def setup_console_tab(self):
        # Command Input
        input_frame = ttk.Frame(self.console_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(input_frame, text="Enter Command:").pack(side=tk.LEFT)
        self.command_entry = ttk.Entry(input_frame, width=50)
        self.command_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(input_frame, text="Execute", command=self.execute_command).pack(side=tk.LEFT, padx=5)

        # Console Output
        output_frame = ttk.LabelFrame(self.console_frame, text="Output")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.console_text = scrolledtext.ScrolledText(output_frame, height=20)
        self.console_text.pack(fill=tk.BOTH, expand=True)

    def add_task(self):
        task_name = self.task_name_entry.get()
        if task_name:
            result = self.assistant.process_command("add_task", task_name)
            messagebox.showinfo("Success", result)
            self.task_name_entry.delete(0, tk.END)
            self.refresh_tasks()
        else:
            messagebox.showwarning("Warning", "Please enter a task name, Sir.")

    def refresh_tasks(self):
        self.tasks_listbox.delete(0, tk.END)
        tasks = self.assistant.process_command("list_tasks")
        if isinstance(tasks, list):
            for task in tasks:
                self.tasks_listbox.insert(tk.END, f"{task['name']} - {task['due_date']}")

    def send_message(self):
        recipient = self.recipient_entry.get()
        message = self.message_entry.get()
        if recipient and message:
            result = self.assistant.process_command("send_message", recipient, message)
            self.messages_text.insert(tk.END, f"To {recipient}: {message}\n")
            self.recipient_entry.delete(0, tk.END)
            self.message_entry.delete(0, tk.END)

    def store_memory(self):
        category = self.memory_category.get()
        data = self.memory_data_entry.get()
        if category and data:
            result = self.assistant.process_command("store_memory", category, data)
            self.memory_text.insert(tk.END, f"[{category}] {data}\n")
            self.memory_data_entry.delete(0, tk.END)

    def execute_command(self):
        command = self.command_entry.get()
        if command:
            parts = command.split()
            cmd = parts[0]
            args = parts[1:] if len(parts) > 1 else []
            result = self.assistant.process_command(cmd, *args)
            self.console_text.insert(tk.END, f">> {command}\n{result}\n\n")
            self.command_entry.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = StarkAssistantUI(root)
    root.mainloop()