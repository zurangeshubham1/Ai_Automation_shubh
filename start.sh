#!/bin/bash
# Start xvfb in background
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
# Wait a moment for xvfb to start
sleep 2
# Start the application
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
