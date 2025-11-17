# Personal Expense Tracker

A simple yet powerful expense tracking application built with Flask backend and modern frontend technologies.

## Features

- Dashboard with income, expense, and balance summary
- Add, view, and delete expenses
- Filter expenses by category and type
- Analytics with charts and category breakdown
- Dark mode support
- Currency selection
- Responsive design for mobile and desktop
- Real-time updates

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite (local, lightweight)
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Bootstrap 5
- **Charts**: Chart.js
- **Icons**: Font Awesome

## Project Structure

\`\`\`
expense-tracker/
├── index.html                 # Main HTML file
├── static/
│   ├── css/
│   │   └── style.css         # Application styles
│   └── js/
│       └── app.js            # Frontend logic
├── app.py                     # Flask main application
├── config.py                  # Configuration file
├── init_db.py                 # Database initialization
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── run.sh                     # Linux/Mac startup script
├── run.bat                    # Windows startup script
└── README.md                  # This file
\`\`\`

## Installation

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Setup

1. Clone or download the project
2. Install Python dependencies:
   \`\`\`bash
   pip install -r requirements.txt
   \`\`\`

3. Initialize the database (optional - adds sample data):
   \`\`\`bash
   python init_db.py
   \`\`\`

## Running the Application

### Option 1: Direct Python

1. Start the Flask backend:
   \`\`\`bash
   python app.py
   \`\`\`

2. Open `index.html` in your web browser or serve it using:
   \`\`\`bash
   python -m http.server 8000
   \`\`\`

3. Access the application at `http://localhost:8000`

### Option 2: Using Startup Scripts

**On Linux/Mac:**
\`\`\`bash
./run.sh
\`\`\`

**On Windows:**
\`\`\`bash
run.bat
\`\`\`

## API Endpoints

### Get All Expenses
\`\`\`
GET /api/expenses
\`\`\`

### Add Expense
\`\`\`
POST /api/expenses
Content-Type: application/json

{
  "description": "Groceries",
  "amount": 45.50,
  "category": "Food",
  "date": "2024-01-15",
  "type": "expense"
}
\`\`\`

### Delete Expense
\`\`\`
DELETE /api/expenses/{id}
\`\`\`

### Delete All Expenses
\`\`\`
DELETE /api/expenses
\`\`\`

### Get Statistics
\`\`\`
GET /api/statistics
\`\`\`

### Health Check
\`\`\`
GET /api/health
\`\`\`

## Categories

- Food
- Transport
- Entertainment
- Utilities
- Health
- Other

## Currencies Supported

- USD ($)
- EUR (€)
- GBP (£)
- INR (₹)

## Features Guide

### Dashboard
- View income, expense, and balance summaries
- Quick access to add new transactions
- Recent transactions display

### Expenses
- View all transactions in table format
- Filter by category and transaction type
- Delete individual transactions

### Analytics
- Category-wise spending breakdown (Pie chart)
- Monthly income vs expenses (Bar chart)
- Detailed category breakdown with percentages

### Settings
- Change currency
- Clear all data

## Deployment

### Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables in Render dashboard
4. Deploy

### Railway

1. Create new project on Railway
2. Connect GitHub repository
3. Set environment variables
4. Deploy

### AWS EC2

1. Launch an EC2 instance (Ubuntu 20.04 or similar)
2. SSH into instance
3. Install Python and dependencies
4. Clone repository
5. Run application using a production WSGI server:
   \`\`\`bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   \`\`\`

## Development

To run in development mode:

\`\`\`bash
export FLASK_ENV=development
python app.py
\`\`\`

## Customization

### Add New Categories

Edit `index.html` and update the category select options:

\`\`\`html
<select class="form-control" id="category" required>
    <option value="">Select category</option>
    <option value="Your New Category">Your New Category</option>
</select>
\`\`\`

### Change Colors

Edit `static/css/style.css` and modify the CSS variables in `:root`:

\`\`\`css
:root {
    --primary-color: #2563eb;
    --success-color: #10b981;
    --danger-color: #ef4444;
    /* ... other colors */
}
\`\`\`

## Troubleshooting

### CORS Issues
If you encounter CORS errors, ensure the Flask backend is running and the `API_URL` in `app.js` matches your backend address.

### Database Errors
Delete `expenses.db` and run `init_db.py` again to reinitialize.

### Port Already in Use
Change the port in `app.py` or `run.sh` scripts.

## License

This project is open source and available for personal use.

## Support

For issues and feature requests, please check the code or refer to the documentation.
