#!/bin/bash

# Script to reset the system to genesis and restart all services fresh

echo "Stopping running services..."

# Find and kill REST API server process
REST_API_PID=$(pgrep -f "python3 api_gateway/rest_endpoints.py")
if [ -n "$REST_API_PID" ]; then
  echo "Killing REST API server (PID $REST_API_PID)..."
  kill $REST_API_PID
else
  echo "REST API server not running."
fi

# Find and kill WebSocket server process
WS_SERVER_PID=$(pgrep -f "python3 api_gateway/websocket_server.py")
if [ -n "$WS_SERVER_PID" ]; then
  echo "Killing WebSocket server (PID $WS_SERVER_PID)..."
  kill $WS_SERVER_PID
else
  echo "WebSocket server not running."
fi

# Find and kill Mining backend process
MINING_BACKEND_PID=$(pgrep -f "python3 mining_backend.py")
if [ -n "$MINING_BACKEND_PID" ]; then
  echo "Killing Mining backend (PID $MINING_BACKEND_PID)..."
  kill $MINING_BACKEND_PID
else
  echo "Mining backend not running."
fi

# Wait a moment to ensure processes are stopped
sleep 3

echo "Starting all services fresh using quickstart.sh..."
chmod +x quickstart.sh
./quickstart.sh

echo "Reset and restart complete. The system is now starting from genesis."
