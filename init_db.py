import sqlite3
from config import DATABASE
import os
from datetime import date, timedelta

SCHEMA = """
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income','expense'))
);
"""

SAMPLE_DATA = [
    ("Salary", 1200.00, "Income", (date.today() - timedelta(days=40)).isoformat(), "income"),
    ("Groceries", 45.50, "Food", (date.today() - timedelta(days=10)).isoformat(), "expense"),
    ("Bus pass", 20.00, "Transport", (date.today() - timedelta(days=9)).isoformat(), "expense"),
    ("Movie night", 12.25, "Entertainment", (date.today() - timedelta(days=7)).isoformat(), "expense"),
    ("Freelance", 200.00, "Income", (date.today() - timedelta(days=5)).isoformat(), "income"),
]

def init_db():
    # ensure dir exists
    db_dir = os.path.dirname(DATABASE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.executescript(SCHEMA)
    conn.commit()

    # insert sample data only if table empty
    cur.execute('SELECT COUNT(*) FROM expenses')
    count = cur.fetchone()[0]
    if count == 0:
        for desc, amt, cat, dt, typ in SAMPLE_DATA:
            cur.execute('INSERT INTO expenses (description, amount, category, date, type) VALUES (?, ?, ?, ?, ?)', (desc, amt, cat, dt, typ))
        conn.commit()
        print('Inserted sample data into', DATABASE)
    else:
        print('Database already has data; skipping sample insertion.')

    conn.close()
    print('Database initialized at', DATABASE)

if __name__ == '__main__':
    init_db()
