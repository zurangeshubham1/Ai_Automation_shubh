@echo off
echo 🤖 AI Agent Web Interface Startup
echo ====================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Run the startup script
echo 🚀 Starting AI Agent Web Interface...
python start_web_interface.py

pause
