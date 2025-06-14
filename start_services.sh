#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

# Kill existing processes if pid files exist
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null || true
    rm backend.pid
fi

if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null || true
    rm frontend.pid
fi

echo "Starting backend service..."
cd backend
# Install Python dependencies using Poetry
poetry install
# Start the Python backend server
poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8000 > ../logs/backend.log 2>&1 &
echo $! > ../backend.pid
cd ..

echo "Starting frontend service..."
cd frontend
npm install
npm run dev > ../logs/frontend.log 2>&1 &
echo $! > ../frontend.pid
cd ..

echo "Services started. PIDs saved in backend.pid and frontend.pid"
echo "Logs available in logs/backend.log and logs/frontend.log"

# Function to check if a process is running
check_process() {
    if [ -f "$1" ]; then
        if kill -0 $(cat "$1") 2>/dev/null; then
            return 0
        fi
        return 1
    fi
    return 1
}

# Wait a few seconds and verify services are running
sleep 5
if check_process "backend.pid" && check_process "frontend.pid"; then
    echo -e "\nAll services are running successfully!"
    echo -e "\nService URLs:"
    echo "Backend API: http://localhost:8000"
    echo "Frontend: http://localhost:5173"
    echo -e "\nTo stop the services, run: ./stop_services.sh"
else
    echo "Warning: One or more services may have failed to start. Check the logs for details."
    exit 1
fi 