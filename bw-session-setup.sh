#!/usr/bin/env zsh
#
# Bitwarden Session Setup
# Unlocks your Bitwarden vault and saves the session token to ~/.bw_session
# Run this once after logging in, or when your session expires
#

SESSION_FILE="$HOME/.bw_session"

echo "Bitwarden Session Setup"
echo "======================="
echo ""

# Check if already logged in
STATUS=$(bw status 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [[ "$STATUS" == "unauthenticated" ]]; then
    echo "You are not logged in to Bitwarden."
    echo "Run: bw login"
    exit 1
fi

if [[ "$STATUS" == "unlocked" ]]; then
    echo "Vault is already unlocked!"
    # Try to get existing session
    if [[ -n "$BW_SESSION" ]]; then
        echo "$BW_SESSION" > "$SESSION_FILE"
        chmod 600 "$SESSION_FILE"
        echo "Session saved to $SESSION_FILE"
        exit 0
    fi
fi

echo "Unlocking Bitwarden vault..."
echo "(Enter your master password)"
echo ""

# Unlock and capture session
SESSION=$(bw unlock --raw 2>/dev/null)

if [[ -n "$SESSION" ]]; then
    echo "$SESSION" > "$SESSION_FILE"
    chmod 600 "$SESSION_FILE"
    echo ""
    echo "Session saved to $SESSION_FILE"
    echo "File permissions set to 600 (owner read/write only)"
    echo ""
    echo "The HIBP dashboard will now automatically use this session."
    echo ""
    echo "Note: Sessions expire after inactivity. Re-run this script if needed."
else
    echo "Failed to unlock vault. Check your master password."
    exit 1
fi
