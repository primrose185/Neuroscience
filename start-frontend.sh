#!/bin/bash

# Ensure logs directory exists
mkdir -p logs

# Kill previous frontend process if running
if [ -f frontend.pid ]; then
    OLD_PID=$(cat frontend.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo "Killing previous frontend process (PID $OLD_PID)"
        kill $OLD_PID
    fi
    rm frontend.pid
fi

# Start frontend in background, log output, save PID
nohup npm run dev > logs/frontend.log 2>&1 &
echo $! > frontend.pid

echo "Frontend started with PID $(cat frontend.pid). Logs: logs/frontend.log"

FRONTEND_URL="http://localhost:5173"
echo "Local address: $FRONTEND_URL" 