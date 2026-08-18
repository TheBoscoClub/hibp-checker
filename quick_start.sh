#!/bin/bash

# HIBP Quick Start & Test Script
# Uses HIBP's test accounts to verify everything works before using real data
#
# ⚡ Powered by Have I Been Pwned (https://haveibeenpwned.com) by Troy Hunt
#    Licensed under Creative Commons Attribution 4.0 International (CC BY 4.0)
#    https://creativecommons.org/licenses/by/4.0/
#
# Prerequisites:
#    - Requires Have I Been Pwned API subscription (Pwned 1-4 tier)
#    - Get API Key: https://haveibeenpwned.com/API/Key

set -euo pipefail

echo "================================================"
echo "HIBP Comprehensive Checker - Quick Start & Test"
echo "================================================"
echo ""

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "Install with: apt-get install python3 python3-pip"
    exit 1
fi

# Check for requests module
if ! python3 -c "import requests" 2>/dev/null; then
    echo "📦 Installing required Python module: requests"
    pip3 install --user requests || {
        echo "❌ Failed to install requests module"
        echo "Try: pip3 install requests"
        exit 1
    }
fi

# Make scripts executable
chmod +x hibp_workflow.sh hibp_comprehensive_checker.py 2>/dev/null || true

echo "✅ Dependencies verified"
echo ""

# Test with HIBP's official test accounts
echo "🧪 Testing with HIBP test accounts..."
echo "These are special accounts provided by HIBP for testing:"
echo ""

# Create test email file
cat > test_emails.txt << 'EOF'
account-exists@hibp-integration-tests.com
multiple-breaches@hibp-integration-tests.com
spam-list-only@hibp-integration-tests.com
stealer-log@hibp-integration-tests.com
sensitive-breach@hibp-integration-tests.com
EOF

echo "Test accounts created in test_emails.txt:"
cat test_emails.txt
echo ""

# The single canonical credential store (~/.claude/rules/security.md).
CANONICAL_KEY_STORE="${HIBP_KEY_STORE:-$HOME/.config/api-keys.env}"

# Check the canonical store FIRST. Sourced in a subshell so only this one
# value crosses — the store holds every credential on the host, and pulling
# all of them into this shell is the fan-out that bd cachyos-sentinel-2miz
# was filed on.
if [[ -r "$CANONICAL_KEY_STORE" ]]; then
    API_KEY="$(
        set +u
        # shellcheck disable=SC1090
        . "$CANONICAL_KEY_STORE" >/dev/null 2>&1 || true
        printf '%s' "${HIBP_API_KEY:-}"
    )"
    [[ -n "$API_KEY" ]] && echo "✅ Found API key in $CANONICAL_KEY_STORE"
fi

# Fall back to a key left in the config file by an older setup.
if [[ -z "${API_KEY:-}" ]] && [[ -f "hibp_config.conf" ]]; then
    source hibp_config.conf
    if [[ -n "$HIBP_API_KEY" ]]; then
        echo "⚠️  Found API key in hibp_config.conf — move it to $CANONICAL_KEY_STORE"
        echo "    A second copy drifts silently at the next rotation."
        API_KEY="$HIBP_API_KEY"
    fi
fi

if [[ -z "${API_KEY:-}" ]]; then
    echo "📝 API Key Required"
    echo "You can use a test key for these test accounts: 00000000000000000000000000000000"
    echo "Or enter your actual HIBP API key for full functionality:"
    read -rp "API Key: " API_KEY
    echo ""
fi

# Run test with test accounts
echo "🚀 Running comprehensive check on test accounts..."
echo "================================================"

python3 hibp_comprehensive_checker.py \
    -k "$API_KEY" \
    --email-file test_emails.txt \
    -o text \
    -v

echo ""
echo "================================================"
echo "✅ Test Complete!"
echo ""

# Offer to set up with real data
read -rp "Would you like to set up the tool with your real email addresses? (y/n): " setup_real

if [[ "$setup_real" == "y" ]]; then
    echo ""
    echo "Setting up for real usage..."
    echo ""
    
    # Create config if it doesn't exist
    if [[ ! -f "hibp_config.conf" ]]; then
        cat > hibp_config.conf << EOF
# HIBP Configuration File
# The API key is deliberately NOT stored here. It lives only in the canonical
# store (~/.config/api-keys.env) and is read on demand.
HIBP_API_KEY=""
EMAIL_ADDRESSES=""
EMAIL_FILE=""
PASSWORDS=""
PASSWORD_FILE=""
OUTPUT_FORMAT="text"
VERBOSE=true
SEND_NOTIFICATIONS=false
NOTIFICATION_EMAIL=""
SLACK_WEBHOOK=""
ENABLE_SCHEDULED_CHECKS=false
SCHEDULE="0 3 * * *"
KEEP_REPORTS=30
TRIGGER_ON_PASSWORD_EXPOSURE=true
TRIGGER_ON_CRITICAL_SITES=true
TRIGGER_ON_NEW_BREACHES=true
NOTIFY_ONLY_NEW=true
RATE_LIMIT_DELAY=1.5
EOF
        echo "✅ Configuration file created: hibp_config.conf"
    fi
    
    # The API key is deliberately NOT written into hibp_config.conf. It
    # belongs in the canonical store only; a copy here would be a second
    # source of truth that goes stale at the next rotation while still
    # looking valid.
    if ! grep -q "^HIBP_API_KEY=" "$CANONICAL_KEY_STORE" 2>/dev/null; then
        echo ""
        echo "⚠️  Add your key to the canonical store before running a check:"
        echo "      # Have I Been Pwned — API key for hibp-checker breach lookups"
        echo "      HIBP_API_KEY=<your key>"
        echo "    in $CANONICAL_KEY_STORE   (then: chmod 600 \"$CANONICAL_KEY_STORE\")"
    fi
    
    echo ""
    echo "How would you like to configure your email addresses?"
    echo "1) Enter a few email addresses directly (1-5 emails)"
    echo "2) Create a file with many email addresses (recommended for 5+ emails)"
    echo "3) I'll configure this manually later"
    echo ""
    read -rp "Choose option (1/2/3): " email_choice
    
    case "$email_choice" in
        1)
            echo ""
            echo "Enter your email addresses (space-separated):"
            echo "Example: bosco@personal.com admin@work.com noreply@service.com"
            read -rp "Emails: " emails
            
            if [[ -n "$emails" ]]; then
                sed -i "s/^EMAIL_ADDRESSES=.*/EMAIL_ADDRESSES=\"$emails\"/" hibp_config.conf
                echo "✅ Email addresses saved to configuration"
                
                # Count emails
                email_count=$(echo "$emails" | wc -w)
                echo "📧 Configured $email_count email address(es)"
            fi
            ;;
        2)
            echo ""
            echo "Creating email list file: my_emails.txt"
            
            cat > my_emails.txt << 'EOF'
# HIBP Email Monitoring List
# ===========================
# Add one email address per line
# Lines starting with # are ignored
#
# Examples:
# personal@gmail.com
# work@company.com
# admin@myservice.com

EOF
            
            echo "Enter email addresses (one per line, empty line when done):"
            while IFS= read -r email; do
                [[ -z "$email" ]] && break
                echo "$email" >> my_emails.txt
            done
            
            sed -i "s|^EMAIL_FILE=.*|EMAIL_FILE=\"./my_emails.txt\"|" hibp_config.conf
            
            # Count emails
            email_count=$(grep -c '@' my_emails.txt 2>/dev/null || echo 0)
            echo "✅ Added $email_count email address(es) to my_emails.txt"
            echo "📝 You can edit my_emails.txt anytime to add/remove emails"
            ;;
        3)
            echo "📝 You can configure emails later by editing hibp_config.conf"
            ;;
    esac
    
    echo ""
    echo "Would you like to enable automatic daily checks?"
    read -rp "Enable scheduled checks? (y/n) [y]: " enable_schedule
    
    if [[ "${enable_schedule:-y}" == "y" ]]; then
        sed -i "s/^ENABLE_SCHEDULED_CHECKS=.*/ENABLE_SCHEDULED_CHECKS=true/" hibp_config.conf
        
        echo ""
        echo "When should checks run?"
        echo "1) Daily at 3 AM (recommended)"
        echo "2) Daily at custom time"
        echo "3) Weekly"
        echo "4) Custom schedule"
        
        read -rp "Choose (1/2/3/4) [1]: " schedule_choice
        
        case "${schedule_choice:-1}" in
            1)
                schedule="0 3 * * *"
                echo "✅ Will check daily at 3 AM"
                ;;
            2)
                read -rp "Enter hour (0-23): " hour
                schedule="0 ${hour} * * *"
                echo "✅ Will check daily at ${hour}:00"
                ;;
            3)
                read -rp "Day of week (0=Sun, 1=Mon, etc): " day
                read -rp "Hour (0-23): " hour
                schedule="0 ${hour} * * ${day}"
                echo "✅ Will check weekly"
                ;;
            4)
                read -rp "Enter cron expression: " schedule
                echo "✅ Custom schedule set"
                ;;
        esac
        
        sed -i "s|^SCHEDULE=.*|SCHEDULE=\"$schedule\"|" hibp_config.conf
        
        # Setup cron
        ./hibp_workflow.sh schedule
    fi
    
    echo ""
    echo "🎉 Setup complete!"
    echo ""
    echo "You can now run checks with:"
    echo "  ./hibp_workflow.sh check"
    echo ""
    echo "Or use with Claude Code:"
    echo "  claude-code run ./hibp_workflow.sh check"
    echo ""
    
    read -rp "Run a check now? (y/n): " run_now
    if [[ "$run_now" == "y" ]]; then
        ./hibp_workflow.sh check
    fi
else
    echo ""
    echo "📚 Next Steps:"
    echo ""
    echo "1. Get your API key from: https://haveibeenpwned.com/API/Key"
    echo "2. Run setup: ./hibp_workflow.sh setup"
    echo "3. Run checks: ./hibp_workflow.sh check"
    echo ""
    echo "For Claude Code integration:"
    echo "  claude-code run ./hibp_workflow.sh check"
fi

echo ""
echo "📖 Full documentation available in README.md"
echo ""

# Cleanup test file
read -rp "Keep test_emails.txt for reference? (y/n): " keep_test
if [[ "$keep_test" != "y" ]]; then
    rm -f test_emails.txt
    echo "Test file removed"
fi

echo ""
echo "Happy hunting, Bosco! 🔍"
