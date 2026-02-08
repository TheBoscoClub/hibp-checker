#!/usr/bin/env zsh
#
# HIBP Dashboard Startup Script
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"

# Source BW_SESSION from persistent file if it exists
if [[ -f "$HOME/.bw_session" ]]; then
    BW_SESSION=$(cat "$HOME/.bw_session")
    export BW_SESSION
fi

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
