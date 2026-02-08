#!/usr/bin/env zsh
#
# HIBP Dashboard Startup Script for macOS
#

set -euo pipefail

echo "================================================"
echo "HIBP Dashboard - macOS Startup"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    echo "Please install Python from https://www.python.org/downloads/"
    echo "Or use Homebrew: brew install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✓ Found: $PYTHON_VERSION"

# Check if pip is installed
if ! python3 -m pip --version &> /dev/null; then
    echo "❌ pip not found!"
    echo "Installing pip..."
    python3 -m ensurepip --upgrade
fi

# Check if Flask is installed
echo "Checking for Flask..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "Flask not installed. Installing..."
    python3 -m pip install --user flask
    echo "✓ Flask installed successfully!"
else
    echo "✓ Flask is installed"
fi

# Get script directory
SCRIPT_DIR="${0:A:h}"

echo ""
echo "Starting HIBP Dashboard..."
echo "Dashboard will be available at: http://127.0.0.1:5000"
echo "Press Ctrl+C to stop"
echo ""

# Start the dashboard
cd "$SCRIPT_DIR"
python3 app.py
