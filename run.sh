#!/bin/bash

# Personal Expense Tracker - Startup Script for Linux/Mac

echo "Starting Personal Expense Tracker..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip3."
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt

# Initialize database (optional)
read -p "Do you want to initialize the database with sample data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Initializing database..."
    python3 init_db.py
fi

# Start Flask backend
echo ""
echo "Starting Flask backend on http://localhost:5000"
echo "Frontend will be available at http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the servers"
echo ""

# Start backend in background
python3 app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend server
python3 -m http.server 8000

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
