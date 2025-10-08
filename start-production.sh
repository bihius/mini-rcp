#!/bin/bash
# MINI RCP Production Startup Script for Linux
# This script starts both the web server and processor services

echo "Starting MINI RCP Production Services..."

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install uv first."
    echo "Visit: https://github.com/astral-sh/uv"
    exit 1
fi

# Function to start service in background
start_service() {
    local name="$1"
    local command="$2"
    local log_file="$3"

    echo "Starting $name..."
    nohup uv run $command > "$log_file" 2>&1 &
    echo $! > "${name}.pid"
    echo "$name started with PID $(cat ${name}.pid)"
}

# Start the web server
start_service "web-server" "python -m app.web" "logs/web.log"

# Start the processor
start_service "processor" "python -m app.processor" "logs/processor.log"

echo ""
echo "MINI RCP services started successfully!"
echo "Web server: http://localhost:5000"
echo "Check logs/web.log and logs/processor.log for details"
echo ""
echo "To stop services, run: ./stop-production.sh"
echo "Or kill PIDs: $(cat web-server.pid) $(cat processor.pid)"