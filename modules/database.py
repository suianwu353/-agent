import sqlite3


def init_db():
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_content TEXT NOT NULL,
        reminder_time TIMESTAMP NOT NULL,
        status TEXT DEFAULT 'pending',
        location TEXT,
        weather_info TEXT
    )
    ''')
    conn.commit()
    conn.close()

def add_task_to_db(task_content, reminder_time, location=None, weather_info=None):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tasks (task_content, reminder_time, location, weather_info)
        VALUES (?, ?, ?, ?)
    ''', (task_content, reminder_time, location, weather_info))
    conn.commit()
    conn.close()