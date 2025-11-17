from app import create_app
from models import db, Expense
from datetime import date, timedelta

app = create_app()

def init_db():
    with app.app_context():
        db.create_all()

        if Expense.query.first():
            print("Database already populated.")
            return

        samples = [
            ("Salary", 1500, "Income", date.today() - timedelta(days=30), "income"),
            ("Groceries", 150, "Food", date.today() - timedelta(days=5), "expense"),
            ("Transport", 50, "Transport", date.today() - timedelta(days=3), "expense"),
        ]

        for desc, amt, cat, dt, typ in samples:
            e = Expense(
                description=desc,
                amount=amt,
                category=cat,
                date=dt,
                type=typ
            )
            db.session.add(e)

        db.session.commit()
        print("Inserted sample data.")

if __name__ == "__main__":
    init_db()
