#!/bin/bash

# Quickstart script to launch AquiMatrix services with PYTHONPATH set

export PYTHONPATH=$(pwd)

echo "Starting REST API server on port 9000..."
nohup python3 api_gateway/rest_endpoints.py > rest_api.log 2>&1 &

echo "Starting WebSocket server on port 9001..."
nohup python3 api_gateway/websocket_server.py > websocket_server.log 2>&1 &

echo "Starting Mining backend..."
nohup python3 mining_backend.py > mining_backend.log 2>&1 &

echo "All services started in the background."
echo "Logs:"
echo "  REST API: rest_api.log"
echo "  WebSocket Server: websocket_server.log"
echo "  Mining Backend: mining_backend.log"

echo ""
echo "Use the CLI tool to interact with the network:"
echo "  python client_interfaces/cli_commands.py --help"
echo ""
echo "Press Ctrl+C to stop this script. To stop the services, kill the background processes manually."
