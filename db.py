import sqlite3
import os

DB_PATH = os.getenv('DB_PATH', '/root/git/valetudo_heatmap/valetudo.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS robot_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            value INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print('Database initialized.')
