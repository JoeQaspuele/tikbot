import sqlite3
from settings import DB_NAME

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            middle_name TEXT,
            base_city TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(telegram_id, first_name, last_name, middle_name, base_city):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (telegram_id, first_name, last_name, middle_name, base_city)
        VALUES (?, ?, ?, ?, ?)
    ''', (telegram_id, first_name, last_name, middle_name, base_city))
    conn.commit()
    conn.close()

def user_exists(telegram_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM users WHERE telegram_id = ?", (telegram_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists
