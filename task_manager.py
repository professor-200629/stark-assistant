import json
from datetime import datetime

class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task_name, deadline=None, priority='normal'):
        """Add a new task"""
        task = {
            'id': len(self.tasks) + 1,
            'name': task_name,
            'deadline': deadline,
            'priority': priority,
            'completed': False,
            'created_at': datetime.now().isoformat()
        }
        self.tasks.append(task)
        return f"Task '{task_name}' added successfully, Sir."

    def list_tasks(self, filter_by='all'):
        """List all tasks"""
        if filter_by == 'completed':
            return [t for t in self.tasks if t['completed']]
        elif filter_by == 'pending':
            return [t for t in self.tasks if not t['completed']]
        return self.tasks

    def complete_task(self, task_id):
        """Mark a task as complete"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                return f"Task '{task['name']}' completed, Sir."
        return "Task not found, Sir."

    def delete_task(self, task_id):
        """Delete a task"""
        self.tasks = [t for t in self.tasks if t['id'] != task_id]
        return "Task deleted, Sir."

    def get_task(self, task_id):
        """Get a specific task"""
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None

    def set_reminder(self, task_id, reminder_time):
        """Set a reminder for a task"""
        task = self.get_task(task_id)
        if task:
            task['reminder'] = reminder_time
            return f"Reminder set for '{task['name']}', Sir."
        return "Task not found, Sir."

if __name__ == '__main__':
    manager = TaskManager()
    print(manager.add_task('Buy groceries', '2026-02-15', 'high'))
    print(manager.add_task('Finish project', '2026-02-20', 'normal'))
    print(manager.list_tasks())
    print(manager.complete_task(1))