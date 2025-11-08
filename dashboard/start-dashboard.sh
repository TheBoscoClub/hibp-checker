#!/bin/bash
#
# HIBP Dashboard Startup Script
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Flask is not installed. Installing..."
    pip3 install --user flask
fi

# Start the dashboard
echo "Starting HIBP Dashboard..."
echo "Dashboard will be available at: http://127.0.0.1:5000"
echo "Press Ctrl+C to stop"
echo ""

cd "$SCRIPT_DIR"
python3 app.py
