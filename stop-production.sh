#!/bin/bash
# MINI RCP Production Stop Script for Linux

echo "Stopping MINI RCP Production Services..."

# Function to stop service
stop_service() {
    local name="$1"
    local pid_file="${name}.pid"

    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        echo "Stopping $name (PID: $pid)..."
        kill "$pid" 2>/dev/null || echo "Process $pid not found or already stopped"
        rm -f "$pid_file"
    else
        echo "$name PID file not found"
    fi
}

# Stop services
stop_service "web-server"
stop_service "processor"

echo ""
echo "MINI RCP services stopped."
echo "Check logs for any remaining processes."