import schedule
import time

class AutomationManager:
    def __init__(self):
        self.jobs = []

    def add_job(self, job, schedule_time):
        self.jobs.append((job, schedule_time))
        schedule.every().day.at(schedule_time).do(job)

    def run_jobs(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

# Example job function

def example_job():
    print("Job executed!")

if __name__ == '__main__':
    manager = AutomationManager()
    manager.add_job(example_job, '05:10')  # Adjust time as necessary
    manager.run_jobs()