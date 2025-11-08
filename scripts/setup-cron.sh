#!/bin/bash
#
# HIBP Checker - Cron Setup Script
#
# ⚡ Powered by Have I Been Pwned (https://haveibeenpwned.com) by Troy Hunt
#    Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
LOG_DIR="${HOME}/.local/share/hibp-checker"
CONFIG_DIR="${HOME}/.config/hibp-checker"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "================================================"
echo "HIBP Checker - Cron Setup"
echo "================================================"
echo ""

# Create directories
echo "Creating directories..."
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
        read -p "Enter your HIBP API key: " api_key
        echo "HIBP_API_KEY=${api_key}" > "${CONFIG_DIR}/hibp-checker.env"
        chmod 600 "${CONFIG_DIR}/hibp-checker.env"
        echo -e "${GREEN}✓${NC} API key saved to ${CONFIG_DIR}/hibp-checker.env"
        echo ""
    fi
fi

# Create wrapper script that sources environment
WRAPPER_SCRIPT="${PROJECT_DIR}/scripts/hibp-cron-wrapper.sh"
cat > "$WRAPPER_SCRIPT" << 'EOF'
#!/bin/bash
# HIBP Checker - Cron Wrapper Script
# This script sources the environment and runs the checker

# Source environment file if it exists
if [[ -f "${HOME}/.config/hibp-checker/hibp-checker.env" ]]; then
    source "${HOME}/.config/hibp-checker/hibp-checker.env"
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Run the checker
cd "$PROJECT_DIR"
"${PROJECT_DIR}/hibp_workflow.sh" check >> "${HOME}/.local/share/hibp-checker/hibp-checker.log" 2>> "${HOME}/.local/share/hibp-checker/hibp-checker.error.log"
EOF

chmod +x "$WRAPPER_SCRIPT"
echo -e "${GREEN}✓${NC} Created wrapper script: $WRAPPER_SCRIPT"
echo ""

# Show cron schedule options
echo "Available cron schedules:"
echo ""
echo "  1. Daily at 3 AM"
echo "  2. Weekly on Monday at 9 AM"
echo "  3. Custom schedule"
echo "  4. Manual setup (skip automatic installation)"
echo ""

read -p "Choice [1-4]: " choice

case $choice in
    1)
        CRON_SCHEDULE="0 3 * * *"
        SCHEDULE_DESC="Daily at 3 AM"
        ;;
    2)
        CRON_SCHEDULE="0 9 * * 1"
        SCHEDULE_DESC="Weekly on Monday at 9 AM"
        ;;
    3)
        echo ""
        echo "Enter custom cron schedule (e.g., '0 2 * * *' for 2 AM daily):"
        echo "Format: minute hour day month weekday"
        read -p "Schedule: " CRON_SCHEDULE
        SCHEDULE_DESC="Custom: $CRON_SCHEDULE"
        ;;
    4)
        echo ""
        echo "To add manually later, edit your crontab with:"
        echo "  crontab -e"
        echo ""
        echo "Add this line:"
        echo "  0 3 * * * ${WRAPPER_SCRIPT}"
        echo ""
        exit 0
        ;;
    *)
        echo -e "${RED}✗${NC} Invalid choice"
        exit 1
        ;;
esac

# Install cron job
echo ""
echo "Installing cron job: $SCHEDULE_DESC"
echo ""

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "hibp-cron-wrapper.sh"; then
    echo -e "${YELLOW}⚠${NC}  Cron job already exists. Removing old entry..."
    crontab -l 2>/dev/null | grep -v "hibp-cron-wrapper.sh" | crontab -
fi

# Add new cron job
(crontab -l 2>/dev/null; echo "${CRON_SCHEDULE} ${WRAPPER_SCRIPT}") | crontab -
echo -e "${GREEN}✓${NC} Cron job installed: $SCHEDULE_DESC"
echo ""

# Verify installation
echo "Current cron jobs for HIBP Checker:"
crontab -l | grep "hibp-cron-wrapper.sh" || echo "None found"
echo ""

echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Useful commands:"
echo "  crontab -l                    # List all cron jobs"
echo "  crontab -e                    # Edit cron jobs"
echo "  tail -f ${LOG_DIR}/hibp-checker.log        # View logs"
echo "  tail -f ${LOG_DIR}/hibp-checker.error.log  # View errors"
echo ""
echo "Logs are saved to:"
echo "  ${LOG_DIR}/hibp-checker.log"
echo "  ${LOG_DIR}/hibp-checker.error.log"
echo ""
echo "To test manually:"
echo "  ${WRAPPER_SCRIPT}"
echo ""
