"""
main_controller.py – Orchestrator for the STARK REST API layer.

This module provides the StarkAssistant class used by api_interface.py and
ui_interface.py.  It wires together TaskManager, CommunicationModule, and
MemoryManager and exposes a process_command() interface for the HTTP API.

NOTE: This is separate from stark/core.py which is the voice-assistant
orchestrator.  This module focuses on the structured command API.
"""

from datetime import datetime

from communication_module import CommunicationModule
from memory import MemoryManager
from task_manager import TaskManager


class StarkAssistant:
    """Main orchestrator module that coordinates all assistant modules."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.task_manager = TaskManager()
        self.communication_manager = CommunicationModule()
        self.memory_manager = MemoryManager()
        self.start_time = datetime.now()
        print(f"Welcome, Sir. I am at your service. Current time: {self.start_time}")

    def process_command(self, command: str, *args):
        """Process user commands and route to the appropriate module."""
        command = command.lower().strip()

        # Task Management Commands
        if command == "add_task":
            return self.task_manager.add_task(
                args[0], self.user_id, args[1] if len(args) > 1 else None
            )
        elif command == "list_tasks":
            return self.task_manager.list_tasks(self.user_id)
        elif command == "complete_task":
            return self.task_manager.complete_task(args[0])
        elif command == "delete_task":
            return self.task_manager.delete_task(args[0])
        elif command == "get_overdue_tasks":
            return self.task_manager.get_overdue_tasks(self.user_id)

        # Communication Commands
        elif command == "send_message":
            return self.communication_manager.send_message(
                args[0], args[1], self.user_id
            )
        elif command == "get_messages":
            return self.communication_manager.get_messages(self.user_id)
        elif command == "send_notification":
            return self.communication_manager.send_notification(
                args[0], self.user_id, args[1] if len(args) > 1 else "notification"
            )
        elif command == "get_notifications":
            return self.communication_manager.get_notifications(self.user_id)

        # Memory Commands — delegates to MemoryManager (memory.py)
        elif command == "store_memory":
            # args: key, value
            return self.memory_manager.store_information(args[0], args[1])
        elif command == "retrieve_memory":
            # args: key
            return self.memory_manager.retrieve_information(args[0])
        elif command == "search_memories":
            # args: query
            return self.memory_manager.search_memories(args[0])

        else:
            return "Command not recognized, Sir. Please try again."

    def get_status(self) -> dict:
        """Return overall assistant status."""
        messages = self.communication_manager.get_messages(self.user_id)
        return {
            "user_id": self.user_id,
            "uptime": str(datetime.now() - self.start_time),
            "active_tasks": len(
                [t for t in self.task_manager.tasks if not t["completed"]]
            ),
            "pending_messages": len(messages) if isinstance(messages, list) else 0,
            "stored_memories": len(self.memory_manager.learned_information),
        }

    def shutdown(self) -> bool:
        """Gracefully shut down the assistant."""
        print("Shutting down. It has been a pleasure serving you, Sir.")
        return True
