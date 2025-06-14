#!/bin/bash

# Function to stop a service
stop_service() {
    local pid_file=$1
    local service_name=$2
    
    if [ -f "$pid_file" ]; then
        echo "Stopping $service_name..."
        kill $(cat "$pid_file") 2>/dev/null || true
        rm "$pid_file"
        echo "$service_name stopped"
    else
        echo "No $service_name PID file found"
    fi
}

# Stop both services
stop_service "backend.pid" "backend service"
stop_service "frontend.pid" "frontend service"

echo "All services stopped" 