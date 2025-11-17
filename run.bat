@echo off
REM Personal Expense Tracker - Startup Script for Windows

echo Starting Personal Expense Tracker...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://www.python.org
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Initialize database (optional)
set /p init="Do you want to initialize the database with sample data? (y/n): "
if /i "%init%"=="y" (
    echo Initializing database...
    python init_db.py
)

REM Start Flask backend
echo.
echo Starting Flask backend on http://localhost:5000
echo Frontend will be available at http://localhost:8000
echo.
echo Close this window to stop the servers
echo.

REM Start backend in new window
start "Flask Backend" python app.py

REM Wait a moment for backend to start
timeout /t 2 /nobreak

REM Start frontend server
python -m http.server 8000
