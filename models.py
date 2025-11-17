from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False, default="Other")
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "description": self.description,
            "amount": float(self.amount),
            "category": self.category,
            "date": self.date.isoformat(),
            "type": self.type
        }
