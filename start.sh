#!/bin/bash

echo "Starting Stock Calendar Service..."
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run initialization first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if uvicorn is already running and kill it to restart fresh
pkill -f "uvicorn main:app" 2>/dev/null

echo "Running background refresh job to update local database..."
# For a production setup, this script (tools/bg_refresh.py) should be placed on a cron job.
# E.g.: 0 * * * * cd /Users/jeff/Desktop/Project/Stock_Calendar && source venv/bin/activate && python tools/bg_refresh.py
python tools/bg_refresh.py

echo "Starting backend server on port 8000..."
# Start server in background
uvicorn main:app --port 8000 &
SERVER_PID=$!

echo "Waiting for server to initialize..."
sleep 2

echo "Opening browser..."
open http://127.0.0.1:8000

echo "Service is running! Press Ctrl+C to stop the server."

# Keep script running to allow easy stopping
wait $SERVER_PID
