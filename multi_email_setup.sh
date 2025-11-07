#!/bin/bash

# HIBP Multi-Email Automation Example
# ====================================
# Complete setup and automation for monitoring multiple email addresses
# Perfect for personal use with Pwned 1 subscription

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "================================================"
echo "HIBP Multi-Email Monitoring Setup"
echo "For Bosco's Automation Workflow"
echo "================================================"
echo ""

# Step 1: Create email list
echo "Step 1: Creating email list file..."
cat > my_emails.txt << 'EOF'
# Personal Email Addresses
# ========================
# Add all your email addresses below
# One per line, comments start with #

# Primary emails
bosco@personal-domain.com
bosco@work-company.com

# Service accounts
admin@my-service.com
support@my-business.com
noreply@automated-system.com

# Legacy emails (old but might be in breaches)
old-email@previous-isp.com
college-email@alumni.edu

# Domain admin accounts
webmaster@my-domain.com
postmaster@my-domain.com
abuse@my-domain.com

EOF

echo "✅ Created my_emails.txt with template"
echo ""

# Step 2: Create configuration
echo "Step 2: Creating configuration..."
cat > hibp_config.conf << 'EOF'
# HIBP Configuration for Multiple Email Monitoring
# =================================================

# API Configuration
HIBP_API_KEY="YOUR-32-CHARACTER-API-KEY-HERE"

# Email Sources (using file for multiple emails)
EMAIL_ADDRESSES=""
EMAIL_FILE="./my_emails.txt"

# Output Settings
OUTPUT_FORMAT="text"
VERBOSE=false
REPORT_DIR="./reports"
LOG_DIR="./logs"

# Automation Settings
ENABLE_SCHEDULED_CHECKS=true
SCHEDULE="0 3 * * *"  # Daily at 3 AM

# Notification Settings
SEND_NOTIFICATIONS=true
NOTIFICATION_EMAIL="bosco@main-email.com"
NOTIFY_ONLY_NEW=true  # Only notify on NEW breaches

# Slack Integration (optional)
SLACK_WEBHOOK=""

# Report Management
KEEP_REPORTS=30  # Keep last 30 reports

# Security Triggers
TRIGGER_ON_PASSWORD_EXPOSURE=true
TRIGGER_ON_CRITICAL_SITES=true
TRIGGER_ON_NEW_BREACHES=true

# Rate Limiting for Pwned 1 (10 req/min)
RATE_LIMIT_DELAY=1.5

# Breach Tracking
LAST_BREACH_FILE="./.last_breach_check"

EOF

echo "✅ Created hibp_config.conf"
echo ""

# Step 3: Prompt for API key
echo "Step 3: API Key Configuration"
echo "-----------------------------"
echo "Get your API key from: https://haveibeenpwned.com/API/Key"
echo ""
read -rp "Enter your HIBP API key: " api_key

# Update config with API key
sed -i "s/YOUR-32-CHARACTER-API-KEY-HERE/$api_key/" hibp_config.conf

echo "✅ API key configured"
echo ""

# Step 4: Customize email list
echo "Step 4: Customize Your Email List"
echo "----------------------------------"
echo "Current template has example emails in my_emails.txt"
echo ""
read -rp "Would you like to edit the email list now? (y/n): " edit_emails

if [[ "$edit_emails" == "y" ]]; then
    # Check for available editors
    if command -v nano >/dev/null 2>&1; then
        nano my_emails.txt
    elif command -v vi >/dev/null 2>&1; then
        vi my_emails.txt
    else
        echo "Please edit my_emails.txt manually with your email addresses"
    fi
fi

# Count emails
email_count=$(grep -v '^#' my_emails.txt | grep '@' | wc -l)
echo "✅ Configured to monitor $email_count email addresses"
echo ""

# Step 5: Test configuration
echo "Step 5: Testing Configuration"
echo "------------------------------"
echo "Running test check on first email..."

# Get first email for test
first_email=$(grep -v '^#' my_emails.txt | grep '@' | head -1)

if [[ -n "$first_email" ]]; then
    python3 hibp_comprehensive_checker.py \
        -k "$api_key" \
        -e "$first_email" \
        -o text \
        -v 2>/dev/null || {
            echo "⚠️ Test failed. Please check:"
            echo "  1. API key is valid"
            echo "  2. Python 3 and requests module are installed"
            echo "  3. Internet connection is working"
            exit 1
        }
    echo "✅ API connection test successful"
else
    echo "⚠️ No valid emails found in my_emails.txt"
fi
echo ""

# Step 6: Run full check
echo "Step 6: Running Full Check"
echo "--------------------------"
read -rp "Run complete check on all emails? (y/n): " run_full

if [[ "$run_full" == "y" ]]; then
    echo "Starting comprehensive check (this may take a few minutes)..."
    ./hibp_workflow.sh check
fi
echo ""

# Step 7: Setup automation
echo "Step 7: Automation Setup"
echo "------------------------"
read -rp "Enable daily automated checks at 3 AM? (y/n): " enable_cron

if [[ "$enable_cron" == "y" ]]; then
    # Create cron entry
    cron_entry="0 3 * * * cd $SCRIPT_DIR && ./hibp_workflow.sh check >> logs/cron.log 2>&1"
    
    # Check if already exists
    if crontab -l 2>/dev/null | grep -q "hibp_workflow.sh"; then
        echo "✅ Scheduled checks already configured"
    else
        (crontab -l 2>/dev/null; echo "$cron_entry") | crontab -
        echo "✅ Daily checks scheduled for 3 AM"
    fi
    
    # Show next run time
    echo "Next scheduled run: tomorrow at 3:00 AM"
fi
echo ""

# Step 8: Create helper scripts
echo "Step 8: Creating Helper Scripts"
echo "--------------------------------"

# Create quick check script
cat > quick_check.sh << 'EOF'
#!/bin/bash
# Quick manual check of all configured emails
cd "$(dirname "$0")"
./hibp_workflow.sh check
EOF
chmod +x quick_check.sh

# Create add email script
cat > add_email.sh << 'EOF'
#!/bin/bash
# Add new email to monitoring list
if [[ -z "$1" ]]; then
    read -rp "Enter email to add: " email
else
    email="$1"
fi
echo "$email" >> my_emails.txt
echo "Added $email to monitoring list"
echo "Total emails monitored: $(grep -c '@' my_emails.txt)"
EOF
chmod +x add_email.sh

# Create status script
cat > check_status.sh << 'EOF'
#!/bin/bash
# Show monitoring status and statistics
echo "HIBP Monitoring Status"
echo "======================"
echo ""
echo "Emails monitored: $(grep -v '^#' my_emails.txt | grep -c '@')"
echo "Last check: $(stat -c %y reports/hibp_report_*.txt 2>/dev/null | tail -1 | cut -d. -f1 || echo 'Never')"
echo "Reports stored: $(ls reports/hibp_report_*.txt 2>/dev/null | wc -l)"
echo ""

if crontab -l 2>/dev/null | grep -q hibp_workflow; then
    echo "✅ Automated checks: ENABLED"
    crontab -l | grep hibp_workflow
else
    echo "❌ Automated checks: DISABLED"
fi

if [[ -f .last_breach_check ]]; then
    echo ""
    echo "Breach tracking: ACTIVE"
    echo "Breaches in last check: $(wc -l < .last_breach_check)"
fi
EOF
chmod +x check_status.sh

echo "✅ Created helper scripts:"
echo "  - quick_check.sh    : Run manual check"
echo "  - add_email.sh      : Add new email to monitoring"
echo "  - check_status.sh   : Show monitoring status"
echo ""

# Step 9: Summary
echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "📊 Configuration Summary:"
echo "  - Monitoring $email_count email addresses"
echo "  - Reports saved to: ./reports/"
echo "  - Logs saved to: ./logs/"
if [[ "$enable_cron" == "y" ]]; then
    echo "  - Automated checks: Daily at 3 AM"
fi
echo ""
echo "🎯 Quick Commands:"
echo "  ./quick_check.sh         - Run check now"
echo "  ./add_email.sh           - Add new email"
echo "  ./check_status.sh        - Show status"
echo "  ./hibp_workflow.sh help  - All commands"
echo ""
echo "📧 Email Management:"
echo "  Edit my_emails.txt to add/remove emails"
echo "  Each email is checked for:"
echo "    • Data breaches"
echo "    • Password exposures"
echo "    • Stealer logs (credential stuffing)"
echo "    • Public paste dumps"
echo ""
echo "🚨 Security Actions:"
echo "  Exit code 0 = No breaches (✅)"
echo "  Exit code 1 = Breaches found (⚠️)"
echo "  Exit code 2 = Passwords compromised (🚨)"
echo ""
echo "Happy monitoring, Bosco! 🔍"
