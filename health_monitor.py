import logging
import time

class HealthMonitor:
    def __init__(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.health_metrics = {}
        self.medication_reminders = []
        self.sessions = []

    def log_health_metric(self, metric_name, value):
        self.health_metrics[metric_name] = value
        logging.info(f'Logged {metric_name}: {value}')

    def add_medication_reminder(self, medication_name, time_to_take):
        reminder = {'medication': medication_name, 'time': time_to_take}
        self.medication_reminders.append(reminder)
        logging.info(f'Added medication reminder: {medication_name} at {time_to_take}')

    def track_work_session(self, session_name):
        start_time = time.time()
        self.sessions.append({'name': session_name, 'start': start_time})
        logging.info(f'Started work session: {session_name} at {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_time))}')

    def end_work_session(self, session_name):
        end_time = time.time()
        for session in self.sessions:
            if session['name'] == session_name:
                session['end'] = end_time
                logging.info(f'Ended work session: {session_name} at {time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(end_time))}')
                break

    def check_health_status(self):
        status = "Health Metrics: " + str(self.health_metrics) + '\n' + "Medication Reminders: " + str(self.medication_reminders)
        logging.info(f'Current Health Status: {status}')
        return status

if __name__ == '__main__':
    monitor = HealthMonitor()  
    monitor.log_health_metric('Heart Rate', 72)  
    monitor.add_medication_reminder('Aspirin', '08:00')  
    monitor.track_work_session('Programming')  
    time.sleep(3)  # Simulating a work session for 3 seconds
    monitor.end_work_session('Programming')  
    monitor.check_health_status()