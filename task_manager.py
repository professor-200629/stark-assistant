class TaskManager:
    def __init__(self):
        self.tasks = []
        self.completed_tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def list_tasks(self):
        return self.tasks

    def complete_task(self, task_id):
        if task_id < len(self.tasks):
            completed = self.tasks.pop(task_id)
            self.completed_tasks.append(completed)

    def delete_task(self, task_id):
        if task_id < len(self.tasks):
            self.tasks.pop(task_id)

    def set_reminder(self, task_id, reminder_time):
        if task_id < len(self.tasks):
            self.tasks[task_id]['reminder'] = reminder_time

    def get_overdue_tasks(self, current_time):
        overdue_tasks = []
        for task in self.tasks:
            if 'reminder' in task and task['reminder'] < current_time:
                overdue_tasks.append(task)
        return overdue_tasks
