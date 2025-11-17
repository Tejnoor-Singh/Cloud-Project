from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from datetime import datetime, date
from config import Config
from models import db, Expense
from flask_migrate import Migrate
import os

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)

    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)
    app.config['JSON_SORT_KEYS'] = False

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/health')
    def health():
        return jsonify({"status": "ok"}), 200

    # -----------------
    # Accept both date formats
    # -----------------
    def parse_date(date_str):
        try:
            # Check DD/MM/YYYY
            if "/" in date_str:
                d, m, y = date_str.split("/")
                return date(int(y), int(m), int(d))
            # ISO format YYYY-MM-DD
            return date.fromisoformat(date_str)
        except:
            raise ValueError("Invalid date format. Use DD/MM/YYYY or YYYY-MM-DD")

    @app.route('/api/expenses', methods=['GET'])
    def get_expenses():
        expenses = Expense.query.order_by(Expense.date.asc(), Expense.id.asc()).all()
        return jsonify([e.to_dict() for e in expenses]), 200

    @app.route('/api/expenses', methods=['POST'])
    def create_expense():
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        try:
            description = data.get("description")
            amount = float(data.get("amount"))
            category = data.get("category")
            date_str = data.get("date")
            type_ = data.get("type")

            if not description or not amount or not date_str or not type_:
                return jsonify({"error": "Missing fields"}), 400

            parsed_date = parse_date(date_str)

            new_expense = Expense(
                description=description,
                amount=amount,
                category=category or "Other",
                date=parsed_date,
                type=type_
            )
            db.session.add(new_expense)
            db.session.commit()

            return jsonify(new_expense.to_dict()), 201

        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        except Exception as e:
            return jsonify({"error": "Server error", "details": str(e)}), 500

    @app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
    def delete_expense(expense_id):
        exp = Expense.query.get_or_404(expense_id)
        db.session.delete(exp)
        db.session.commit()
        return jsonify({"deleted": expense_id}), 200

    @app.route('/api/expenses', methods=['DELETE'])
    def delete_all_expenses():
        db.session.query(Expense).delete()
        db.session.commit()
        return jsonify({"deleted_all": True}), 200

    @app.route('/api/statistics')
    def statistics():
        income = db.session.query(db.func.sum(Expense.amount)).filter(Expense.type == 'income').scalar() or 0
        expense = db.session.query(db.func.sum(Expense.amount)).filter(Expense.type == 'expense').scalar() or 0

        rows = (
            db.session.query(Expense.category, db.func.sum(Expense.amount))
            .filter(Expense.type == "expense")
            .group_by(Expense.category)
            .all()
        )

        return jsonify({
            "income": float(income),
            "expenses": float(expense),
            "balance": float(income - expense),
            "by_category": [{"category": cat, "total": float(val)} for cat, val in rows]
        }), 200

    return app


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000, debug=True)
