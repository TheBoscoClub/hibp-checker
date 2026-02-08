#!/usr/bin/env zsh
#
# HIBP Checker - Systemd Setup Script
#
# ⚡ Powered by Have I Been Pwned (https://haveibeenpwned.com) by Troy Hunt
#    Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

set -euo pipefail

SCRIPT_DIR="${0:A:h}"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SYSTEMD_USER_DIR="${HOME}/.config/systemd/user"
LOG_DIR="${HOME}/.local/share/hibp-checker"
CONFIG_DIR="${HOME}/.config/hibp-checker"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "================================================"
echo "HIBP Checker - Systemd Timer Setup"
echo "================================================"
echo ""

# Create directories
echo "Creating directories..."
mkdir -p "$SYSTEMD_USER_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$CONFIG_DIR"
echo -e "${GREEN}✓${NC} Directories created"
echo ""

# Check for API key
if [[ -z "${HIBP_API_KEY:-}" ]]; then
    echo -e "${YELLOW}⚠${NC}  HIBP_API_KEY not set in environment"
    echo "Please set it in one of:"
    echo "  1. ${CONFIG_DIR}/hibp-checker.env"
    echo "  2. ~/.bashrc or ~/.zshrc"
    echo ""

    read -p "Do you want to create ${CONFIG_DIR}/hibp-checker.env now? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -rp "Enter your HIBP API key: " api_key
        echo "HIBP_API_KEY=${api_key}" > "${CONFIG_DIR}/hibp-checker.env"
        chmod 600 "${CONFIG_DIR}/hibp-checker.env"
        echo -e "${GREEN}✓${NC} API key saved to ${CONFIG_DIR}/hibp-checker.env"
        echo ""
    fi
fi

# Copy and configure service and timer files
echo "Installing systemd units..."
echo "Project directory: ${PROJECT_DIR}"

# Copy service file and substitute project path
sed "s|HIBP_PROJECT_DIR|${PROJECT_DIR}|g" "${PROJECT_DIR}/systemd/hibp-checker.service" > "$SYSTEMD_USER_DIR/hibp-checker.service"
cp "${PROJECT_DIR}/systemd/hibp-checker.timer" "$SYSTEMD_USER_DIR/"
cp "${PROJECT_DIR}/systemd/hibp-checker-weekly.timer" "$SYSTEMD_USER_DIR/"

# Copy dashboard service if dashboard directory exists
if [[ -d "${PROJECT_DIR}/dashboard" ]]; then
    sed "s|HIBP_PROJECT_DIR|${PROJECT_DIR}|g" "${PROJECT_DIR}/dashboard/systemd/hibp-dashboard.service" > "$SYSTEMD_USER_DIR/hibp-dashboard.service"
    echo -e "${GREEN}✓${NC} Dashboard service installed"
fi

echo -e "${GREEN}✓${NC} Systemd units installed"
echo ""

# Reload systemd
echo "Reloading systemd..."
systemctl --user daemon-reload
echo -e "${GREEN}✓${NC} Systemd reloaded"
echo ""

# Show available timers
echo "Available timers:"
echo ""
echo "  1. hibp-checker.timer         - Daily at 3 AM"
echo "  2. hibp-checker-weekly.timer  - Weekly on Monday at 9 AM"
echo ""

# Ask which timer to enable
echo "Which timer would you like to enable?"
echo "  [1] Daily (recommended for active monitoring)"
echo "  [2] Weekly (for less frequent checks)"
echo "  [3] Both"
echo "  [4] None (manual setup later)"
echo ""
read -rp "Choice [1-4]: " choice

case $choice in
    1)
        systemctl --user enable hibp-checker.timer
        systemctl --user start hibp-checker.timer
        echo -e "${GREEN}✓${NC} Daily timer enabled and started"
        ;;
    2)
        systemctl --user enable hibp-checker-weekly.timer
        systemctl --user start hibp-checker-weekly.timer
        echo -e "${GREEN}✓${NC} Weekly timer enabled and started"
        ;;
    3)
        systemctl --user enable hibp-checker.timer
        systemctl --user start hibp-checker.timer
        systemctl --user enable hibp-checker-weekly.timer
        systemctl --user start hibp-checker-weekly.timer
        echo -e "${GREEN}✓${NC} Both timers enabled and started"
        ;;
    4)
        echo "No timers enabled. You can enable them later with:"
        echo "  systemctl --user enable --now hibp-checker.timer"
        ;;
    *)
        echo -e "${RED}✗${NC} Invalid choice"
        exit 1
        ;;
esac

# Ask about dashboard service
if [[ -d "${PROJECT_DIR}/dashboard" ]]; then
    echo ""
    read -p "Enable dashboard service (always-on web interface)? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        systemctl --user enable hibp-dashboard.service
        systemctl --user start hibp-dashboard.service
        # Enable linger so dashboard runs even when logged out
        loginctl enable-linger "$USER" 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Dashboard service enabled and started"
        echo "   Dashboard available at: http://127.0.0.1:5000"
    fi
fi

echo ""
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Useful commands:"
echo "  systemctl --user status hibp-checker.timer"
echo "  systemctl --user list-timers"
echo "  systemctl --user start hibp-checker.service  # Run manually"
echo "  journalctl --user -u hibp-checker.service -f # View logs"
echo ""
if [[ -d "${PROJECT_DIR}/dashboard" ]]; then
echo "Dashboard commands:"
echo "  systemctl --user status hibp-dashboard"
echo "  systemctl --user restart hibp-dashboard"
echo ""
fi
echo "Logs are saved to:"
echo "  ${LOG_DIR}/hibp-checker.log"
echo "  ${LOG_DIR}/hibp-checker.error.log"
echo ""
echo "To test the service now:"
echo "  systemctl --user start hibp-checker.service"
echo ""
