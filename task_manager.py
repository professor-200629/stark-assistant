from datetime import datetime, timedelta

class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task_name, user_id, due_date=None):
        """Add a new task for the user"""
        task = {
            'id': len(self.tasks) + 1,
            'name': task_name,
            'user_id': user_id,
            'created_at': datetime.now(),
            'due_date': due_date,
            'completed': False
        }
        self.tasks.append(task)
        return f"Task '{task_name}' added successfully, Sir."

    def list_tasks(self, user_id):
        """List all tasks for a user"""
        user_tasks = [task for task in self.tasks if task['user_id'] == user_id and not task['completed']]
        if user_tasks:
            return user_tasks
        else:
            return "You have no pending tasks, Sir."

    def complete_task(self, task_id):
        """Mark a task as completed"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                return f"Task '{task['name']}' marked as completed, Sir."
        return "Task not found, Sir."

    def delete_task(self, task_id):
        """Delete a task"""
        self.tasks = [task for task in self.tasks if task['id'] != task_id]
        return "Task deleted, Sir."

    def set_reminder(self, task_id, reminder_time):
        """Set a reminder for a task"""
        for task in self.tasks:
            if task['id'] == task_id:
                task['reminder'] = reminder_time
                return f"Reminder set for '{task['name']}' at {reminder_time}, Sir."
        return "Task not found, Sir."

    def get_overdue_tasks(self, user_id):
        """Get all overdue tasks for a user"""
        user_tasks = [task for task in self.tasks if task['user_id'] == user_id and not task['completed']]
        overdue_tasks = [task for task in user_tasks if task['due_date'] and task['due_date'] < datetime.now()]
        return overdue_tasks if overdue_tasks else "No overdue tasks, Sir."

    def get_upcoming_tasks(self, user_id, days=7):
        """Get upcoming tasks for a user within the specified number of days"""
        user_tasks = [task for task in self.tasks if task['user_id'] == user_id and not task['completed']]
        upcoming_tasks = [task for task in user_tasks if task['due_date'] and datetime.now() <= task['due_date'] <= datetime.now() + timedelta(days=days)]
        return upcoming_tasks if upcoming_tasks else "No upcoming tasks, Sir."