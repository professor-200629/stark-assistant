# Routine and Automation Management

from datetime import datetime

"""
This script manages routine tasks and automation.
"""

def current_info():
    '''Function to retrieve current date, time, and user login.'''
    current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    user_login = 'professor-200629'
    return f'Current Date and Time (UTC - YYYY-MM-DD HH:MM:SS formatted): {current_time}\nCurrent User\'s Login: {user_login}'

if __name__ == '__main__':
    print(current_info())