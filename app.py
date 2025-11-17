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

    # initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    CORS(app)
    app.config['JSON_SORT_KEYS'] = False

    @app.route('/')
    def index():
        # serve the frontend index (move your index.html to templates/)
        return render_template('index.html')

    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route('/api/expenses', methods=['GET'])
    def get_expenses():
        expenses = Expense.query.order_by(Expense.date.asc(), Expense.id.asc()).all()
        return jsonify([e.to_dict() for e in expenses]), 200

    @app.route('/api/expenses', methods=['POST'])
    def create_expense():
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        description = (data.get('description') or '').strip()
        amount = data.get('amount')
        category = data.get('category') or 'Other'
        date_str = data.get('date')
        type_ = data.get('type') or 'expense'

        # Validation
        if not description or amount is None or not date_str:
            return jsonify({"error": "Missing required fields (description, amount, date)"}), 400

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid amount"}), 400

        # parse date (accept ISO format YYYY-MM-DD)
        parsed_date = None
        try:
            # If client sent date portion only
            parsed_date = date.fromisoformat(date_str)
        except Exception:
            # attempt datetime parse fallback
            try:
                parsed_date = datetime.fromisoformat(date_str).date()
            except Exception:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

        new_expense = Expense(
            description=description,
            amount=amount,
            category=category,
            date=parsed_date,
            type=type_
        )
        db.session.add(new_expense)
        db.session.commit()
        return jsonify(new_expense.to_dict()), 201

    @app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
    def delete_expense(expense_id):
        exp = Expense.query.get_or_404(expense_id)
        db.session.delete(exp)
        db.session.commit()
        return jsonify({"deleted": expense_id}), 200

    @app.route('/api/expenses', methods=['DELETE'])
    def delete_all_expenses():
        num = Expense.query.delete()
        db.session.commit()
        return jsonify({"deleted_all": True, "count": num}), 200

    @app.route('/api/statistics', methods=['GET'])
    def statistics():
        # totals
        income_total = db.session.query(db.func.coalesce(db.func.sum(Expense.amount), 0)).filter(Expense.type == 'income').scalar()
        expense_total = db.session.query(db.func.coalesce(db.func.sum(Expense.amount), 0)).filter(Expense.type == 'expense').scalar()
        balance = float(income_total) - float(expense_total)

        # breakdown by category for expenses
        rows = (
            db.session.query(Expense.category, db.func.coalesce(db.func.sum(Expense.amount), 0).label('total'))
            .filter(Expense.type == 'expense')
            .group_by(Expense.category)
            .all()
        )
        by_category = [{"category": r[0], "total": float(r[1])} for r in rows]

        return jsonify({
            "income": float(income_total),
            "expenses": float(expense_total),
            "balance": balance,
            "by_category": by_category
        }), 200

    return app

if __name__ == '__main__':
    # development run
    app = create_app()
    # create DB if not exists (migrations preferred)
    with app.app_context():
        # create tables if they don't exist (safe for quick start)
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config.get('DEBUG', True))
