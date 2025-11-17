from flask import Flask, g, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
import sqlite3
import os
from config import DATABASE, DEBUG

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['JSON_SORT_KEYS'] = False
app.config['DEBUG'] = DEBUG
CORS(app)  # allow front-end to fetch from backend

# ---------- database helpers ----------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite_row_to_dict
    return db

def sqlite_row_to_dict(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ---------- helper utilities ----------
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    lastrowid = cur.lastrowid
    cur.close()
    return lastrowid

# ---------- Routes ----------
@app.route('/')
def index():
    # serve index.html from templates so url_for('static'...) works
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    rows = query_db('SELECT * FROM expenses ORDER BY date ASC, id ASC')
    return jsonify(rows), 200

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400

    description = data.get('description', '').strip()
    amount = data.get('amount')
    category = data.get('category', 'Other')
    date = data.get('date')
    type_ = data.get('type', 'expense')

    # Basic validation
    if not description or amount is None or date is None:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400

    new_id = execute_db(
        'INSERT INTO expenses (description, amount, category, date, type) VALUES (?, ?, ?, ?, ?)',
        (description, amount, category, date, type_)
    )
    expense = query_db('SELECT * FROM expenses WHERE id = ?', (new_id,), one=True)
    return jsonify(expense), 201

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    execute_db('DELETE FROM expenses WHERE id = ?', (expense_id,))
    return jsonify({'deleted': expense_id}), 200

@app.route('/api/expenses', methods=['DELETE'])
def delete_all_expenses():
    execute_db('DELETE FROM expenses')
    return jsonify({'deleted_all': True}), 200

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    # total income, total expense, balance, breakdown by category
    income_row = query_db("SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE type='income'", one=True)
    expense_row = query_db("SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE type='expense'", one=True)
    balance = float(income_row['total']) - float(expense_row['total'])

    # category breakdown for expenses
    rows = query_db("SELECT category, COALESCE(SUM(amount), 0) AS total FROM expenses WHERE type='expense' GROUP BY category")
    return jsonify({
        'income': float(income_row['total']),
        'expenses': float(expense_row['total']),
        'balance': balance,
        'by_category': rows
    }), 200

# Static files are served automatically by Flask from /static, so no extra route needed.

if __name__ == '__main__':
    # create DB file if missing
    if not os.path.exists(DATABASE):
        print('Database not found — run "python init_db.py" to initialize with schema/sample data.')
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])
