#!/bin/bash

echo "🤖 AI Agent Web Interface Startup"
echo "===================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "Please install Python 3.7+ from https://python.org"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo

# Make the script executable
chmod +x start_web_interface.py

# Run the startup script
echo "🚀 Starting AI Agent Web Interface..."
python3 start_web_interface.py
