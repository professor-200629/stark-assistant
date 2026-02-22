"""
main_controller.py – Thin API shim for the STARK REST / UI layer.

Architecture
------------
There are two entry points into STARK:

* **Voice assistant** – ``stark/core.py`` (``StarkAssistant``).  This is the
  canonical AI brain that drives the interactive voice loop.
* **Structured API** – this file.  It exposes a keyword-command interface used
  by ``api_interface.py`` and ``ui_interface.py``.

To prevent the two layers from drifting, all memory operations in this module
delegate to ``stark.memory_store.MemoryStore`` — the same implementation used
by the voice assistant.  That way a fact stored via the API is immediately
visible in the voice loop and vice-versa.

Ownership boundaries
--------------------
* Task management   → ``task_manager.TaskManager``
* Communication     → ``communication_module.CommunicationModule``
* Memory            → ``stark.memory_store.MemoryStore``  (shared with voice)
"""

from datetime import datetime

from communication_module import CommunicationModule
from stark.memory_store import MemoryStore
from task_manager import TaskManager


class StarkAssistant:
    """API-layer orchestrator that coordinates TaskManager, CommunicationModule,
    and the shared MemoryStore."""

    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.task_manager = TaskManager()
        self.communication_manager = CommunicationModule()
        self.memory_store = MemoryStore()  # shared implementation with voice layer
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

        # Memory Commands — delegated to MemoryStore (same as voice layer)
        elif command == "store_memory":
            # args: key, value
            self.memory_store.store(args[0], value=args[1])
            return f"Memory stored, Sir: {args[0]} = {args[1]}"
        elif command == "retrieve_memory":
            # Try exact key first; fall back to best semantic match
            key = args[0]
            exact = self.memory_store.recall_exact(key)
            if exact is not None:
                return exact
            results = self.memory_store.recall(key, top_k=1)
            if results:
                return results[0]["value"]
            return f"No memory found for '{key}', Sir."
        elif command == "search_memories":
            # args: query — returns list of matching facts
            results = self.memory_store.recall(args[0])
            if results:
                return results
            return f"No memories found matching '{args[0]}', Sir."

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
            "stored_memories": len(self.memory_store),
        }

    def shutdown(self) -> bool:
        """Gracefully shut down the assistant."""
        print("Shutting down. It has been a pleasure serving you, Sir.")
        return True
