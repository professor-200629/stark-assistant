import sqlite3

class Database:
    def __init__(self, db_name='stark_assistant.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Create user profiles table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        # Create memory table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            memory_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profiles (id)
        )''')

        # Create tasks table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            task_name TEXT NOT NULL,
            user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profiles (id)
        )''')

        # Create communication logs table
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS communication_logs (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            log TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user_profiles (id)
        )''')

        self.conn.commit()

    def add_user(self, username, email):
        self.cursor.execute('INSERT INTO user_profiles (username, email) VALUES (?, ?)', (username, email))
        self.conn.commit()

    def add_memory(self, user_id, memory_text):
        self.cursor.execute('INSERT INTO memory (user_id, memory_text) VALUES (?, ?)', (user_id, memory_text))
        self.conn.commit()

    def add_task(self, user_id, task_name):
        self.cursor.execute('INSERT INTO tasks (user_id, task_name) VALUES (?, ?)', (user_id, task_name))
        self.conn.commit()

    def add_communication_log(self, user_id, log):
        self.cursor.execute('INSERT INTO communication_logs (user_id, log) VALUES (?, ?)', (user_id, log))
        self.conn.commit()

    def close(self):
        self.conn.close()
