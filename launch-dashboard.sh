#!/bin/bash
#
# HIBP Dashboard Launcher
# This script launches the dashboard and opens the browser
#

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"

# Source BW_SESSION from persistent file if it exists
if [[ -f ~/.bw_session ]]; then
    BW_SESSION=$(cat ~/.bw_session)
    export BW_SESSION
fi

# Navigate to dashboard directory
cd "$SCRIPT_DIR/dashboard"

# Check if dashboard is already running
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "Dashboard is already running!"
    echo "Opening browser..."
    xdg-open http://127.0.0.1:5000 2>/dev/null || open http://127.0.0.1:5000 2>/dev/null || echo "Open http://127.0.0.1:5000 in your browser"
    echo ""
    echo "Press Enter to close this window..."
    read -r
    exit 0
fi

# Start the dashboard in background
echo "Starting HIBP Dashboard..."
./start-dashboard.sh &
DASHBOARD_PID=$!

# Wait for dashboard to start
echo "Waiting for dashboard to start..."
sleep 3

# Open browser (try xdg-open for Linux, open for macOS)
echo "Opening browser..."
xdg-open http://127.0.0.1:5000 2>/dev/null || open http://127.0.0.1:5000 2>/dev/null || echo "Open http://127.0.0.1:5000 in your browser"

echo ""
echo "Dashboard is running at: http://127.0.0.1:5000"
echo "Dashboard PID: $DASHBOARD_PID"
echo ""
echo "Press Enter to stop the dashboard and close this window..."
read -r

# Stop dashboard
kill $DASHBOARD_PID 2>/dev/null || true
echo "Dashboard stopped."
