"""
Initialize database and insert sample rows.
Run: python init_db.py
"""
from app import create_app
from models import db, Expense
from datetime import date, timedelta

app = create_app()

SAMPLE = [
    ("Salary", 1200.00, "Income", (date.today() - timedelta(days=40)).isoformat(), "income"),
    ("Groceries", 45.50, "Food", (date.today() - timedelta(days=10)).isoformat(), "expense"),
    ("Bus pass", 20.00, "Transport", (date.today() - timedelta(days=9)).isoformat(), "expense"),
    ("Movie night", 12.25, "Entertainment", (date.today() - timedelta(days=7)).isoformat(), "expense"),
    ("Freelance", 200.00, "Income", (date.today() - timedelta(days=5)).isoformat(), "income"),
]

def init_db():
    with app.app_context():
        db.create_all()
        # check existing
        if Expense.query.first():
            print("Database already contains rows. Skipping sample insert.")
            return
        for desc, amt, cat, dt_str, typ in SAMPLE:
            dt = date.fromisoformat(dt_str)
            e = Expense(description=desc, amount=amt, category=cat, date=dt, type=typ)
            db.session.add(e)
        db.session.commit()
        print("Inserted sample data.")

if __name__ == "__main__":
    init_db()
