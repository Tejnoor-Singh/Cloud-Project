import os

# Database filename (relative to project root)
DATABASE = os.environ.get('EXPENSES_DB', 'expenses.db')

# Flask debug
DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'
