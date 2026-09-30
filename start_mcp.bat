@echo off
REM Travel Planner - MCP Server Startup Script
echo Starting Travel Planner MCP Server...
echo.

cd /d "%~dp0\backend"

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
echo MCP Server running on stdio...
echo.

python mcp_runner.py
