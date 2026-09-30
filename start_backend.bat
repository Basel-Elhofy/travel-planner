@echo off
REM Travel Planner - Backend Startup Script
echo Starting Travel Planner Backend...
echo.

cd /d "%~dp0\backend"

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo Installing dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Starting FastAPI server on http://localhost:8000
echo API docs available at http://localhost:8000/docs
echo.

python main.py
