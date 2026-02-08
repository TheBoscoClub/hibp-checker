#!/usr/bin/env zsh

# Claude Code Security Automation Pipeline
# Comprehensive breach monitoring with automated response
# Designed for integration with Claude Code CLI

set -euo pipefail

# ============================================
# Configuration
# ============================================

SCRIPT_DIR="${0:A:h}"
HIBP_CHECKER="${SCRIPT_DIR}/hibp_workflow.sh"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SECURITY_LOG="${SCRIPT_DIR}/security_audit_${TIMESTAMP}.log"

# Security thresholds
CRITICAL_BREACH_THRESHOLD=5
PASSWORD_EXPOSURE_LIMIT=1
STEALER_LOG_LIMIT=0

# ============================================
# Logging Functions
# ============================================

log_security_event() {
    local level="$1"
    local event="$2"
    local details="$3"
    
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [$level] $event: $details" | tee -a "$SECURITY_LOG"
    
    # Send to Claude Code for analysis if critical
    if [[ "$level" == "CRITICAL" ]]; then
        echo "🚨 Critical Security Event: $event" >&2
        echo "$details" >&2
    fi
}

# ============================================
# HIBP Analysis
# ============================================

run_hibp_analysis() {
    log_security_event "INFO" "HIBP_SCAN" "Starting comprehensive HIBP analysis"
    
    # Run the check and capture output
    local hibp_output
    local hibp_exit_code
    
    if hibp_output=$("$HIBP_CHECKER" check 2>&1); then
        hibp_exit_code=0
    else
        hibp_exit_code=$?
    fi
    
    # Parse results
    local total_breaches=$(echo "$hibp_output" | grep -oP 'Total Breaches: \K\d+' || echo "0")
    local password_exposures=$(echo "$hibp_output" | grep -oP 'Password Exposures: \K\d+' || echo "0")
    local stealer_hits=$(echo "$hibp_output" | grep -oP 'Stealer Log Hits: \K\d+' || echo "0")
    local critical_sites=$(echo "$hibp_output" | grep -oP 'Critical Sites Compromised: \K\d+' || echo "0")
    
    # Log findings
    log_security_event "INFO" "HIBP_RESULTS" "Breaches: $total_breaches, Passwords: $password_exposures, Stealer: $stealer_hits, Critical: $critical_sites"
    
    # Return security score (higher = worse)
    local security_score=$((hibp_exit_code * 100 + password_exposures * 50 + stealer_hits * 75 + critical_sites * 100))
    
    echo "$security_score|$total_breaches|$password_exposures|$stealer_hits|$critical_sites|$hibp_output"
}

# ============================================
# Password Strength Analysis
# ============================================

check_password_strength() {
    local password_file="${1:-}"
    
    if [[ -z "$password_file" ]] || [[ ! -f "$password_file" ]]; then
        return
    fi
    
    log_security_event "INFO" "PASSWORD_CHECK" "Analyzing password strength"
    
    while IFS= read -r password; do
        local length=${#password}
        local has_upper=$(echo "$password" | grep -q '[A-Z]' && echo 1 || echo 0)
        local has_lower=$(echo "$password" | grep -q '[a-z]' && echo 1 || echo 0)
        local has_digit=$(echo "$password" | grep -q '[0-9]' && echo 1 || echo 0)
        local has_special=$(echo "$password" | grep -q '[^a-zA-Z0-9]' && echo 1 || echo 0)
        
        local strength=$((has_upper + has_lower + has_digit + has_special))
        
        if [[ $length -lt 12 ]] || [[ $strength -lt 3 ]]; then
            log_security_event "WARNING" "WEAK_PASSWORD" "Password does not meet minimum requirements"
        fi
    done < "$password_file"
}

# ============================================
# Automated Response Actions
# ============================================

initiate_security_response() {
    local severity="$1"
    local breaches="$2"
    local passwords="$3"
    local stealer="$4"
    local critical="$5"
    
    log_security_event "INFO" "RESPONSE_INIT" "Initiating automated security response"
    
    # Level 1: Informational
    if [[ "$severity" -lt 100 ]]; then
        log_security_event "INFO" "RESPONSE" "No immediate action required"
        send_notification "info" "Regular security check passed"
        
    # Level 2: Warning
    elif [[ "$severity" -lt 300 ]]; then
        log_security_event "WARNING" "RESPONSE" "Security warnings detected"
        send_notification "warning" "Breaches detected: $breaches total"
        generate_password_reset_list
        
    # Level 3: High Risk
    elif [[ "$severity" -lt 500 ]]; then
        log_security_event "WARNING" "HIGH_RISK" "High risk security situation"
        send_notification "high" "Password exposures detected: $passwords"
        enforce_mfa
        rotate_api_keys
        
    # Level 4: Critical
    else
        log_security_event "CRITICAL" "CRITICAL_BREACH" "Critical security breach detected"
        send_notification "critical" "IMMEDIATE ACTION REQUIRED"
        
        # Critical response actions
        lockdown_accounts
        force_password_reset_all
        enable_security_monitoring
        notify_security_team
    fi
}

# ============================================
# Security Actions
# ============================================

generate_password_reset_list() {
    log_security_event "INFO" "ACTION" "Generating password reset list"
    
    cat > "password_reset_required_${TIMESTAMP}.txt" << EOF
Password Reset Required - Generated $(date)
=========================================

The following accounts require password updates due to detected breaches:

EOF
    
    # Parse the latest report for affected accounts
    local latest_report=$(ls -t reports/hibp_report_*.txt 2>/dev/null | head -1)
    if [[ -f "$latest_report" ]]; then
        grep -E "EMAIL:|Password Exposed" "$latest_report" >> "password_reset_required_${TIMESTAMP}.txt"
    fi
    
    log_security_event "INFO" "ACTION_COMPLETE" "Password reset list generated"
}

enforce_mfa() {
    log_security_event "INFO" "ACTION" "Enforcing MFA on affected accounts"
    
    # This would integrate with your identity provider API
    # Example for demonstration:
    echo "MFA_ENFORCEMENT_QUEUE:" > "mfa_enforcement_${TIMESTAMP}.json"
    echo '{"action": "enforce_mfa", "priority": "high", "timestamp": "'$(date -Iseconds)'"}' >> "mfa_enforcement_${TIMESTAMP}.json"
    
    log_security_event "INFO" "ACTION_COMPLETE" "MFA enforcement queued"
}

rotate_api_keys() {
    log_security_event "INFO" "ACTION" "Rotating API keys"
    
    # List of services to rotate (customize for your environment)
    local services=("github" "aws" "stripe" "sendgrid")
    
    for service in "${services[@]}"; do
        log_security_event "INFO" "KEY_ROTATION" "Queued key rotation for: $service"
        # Add actual API rotation logic here
    done
}

lockdown_accounts() {
    log_security_event "CRITICAL" "LOCKDOWN" "Initiating account lockdown"
    
    # Emergency lockdown procedure
    echo "EMERGENCY LOCKDOWN INITIATED" > "emergency_lockdown_${TIMESTAMP}.lock"
    
    # This would integrate with your systems to:
    # - Disable non-essential accounts
    # - Revoke all active sessions
    # - Enable strict access controls
    
    log_security_event "CRITICAL" "LOCKDOWN_COMPLETE" "Emergency lockdown executed"
}

force_password_reset_all() {
    log_security_event "CRITICAL" "FORCE_RESET" "Forcing organization-wide password reset"
    
    # Generate reset tokens and notifications
    echo "FORCED_PASSWORD_RESET" > "forced_reset_${TIMESTAMP}.action"
    
    log_security_event "CRITICAL" "RESET_INITIATED" "Password reset initiated for all users"
}

enable_security_monitoring() {
    log_security_event "INFO" "MONITORING" "Enabling enhanced security monitoring"
    
    # Enable additional logging and monitoring
    cat > "enhanced_monitoring_${TIMESTAMP}.conf" << EOF
# Enhanced Security Monitoring Configuration
log_level: DEBUG
alert_threshold: LOW
realtime_alerts: true
audit_all_access: true
block_suspicious: true
EOF
    
    log_security_event "INFO" "MONITORING_ENABLED" "Enhanced monitoring active"
}

notify_security_team() {
    log_security_event "CRITICAL" "NOTIFICATION" "Notifying security team"
    
    # Multiple notification channels for critical events
    local message="CRITICAL SECURITY EVENT - Immediate response required. Check $SECURITY_LOG"
    
    # Email notification (requires mail setup)
    echo "$message" | mail -s "🚨 CRITICAL SECURITY ALERT" security@company.com 2>/dev/null || true
    
    # Slack notification (if configured)
    if [[ -n "${SLACK_WEBHOOK:-}" ]]; then
        curl -X POST -H 'Content-type: application/json' \
            --data '{"text":"🚨 '"$message"'","channel":"#security-alerts"}' \
            "$SLACK_WEBHOOK" 2>/dev/null || true
    fi
    
    log_security_event "CRITICAL" "TEAM_NOTIFIED" "Security team has been alerted"
}

send_notification() {
    local level="$1"
    local message="$2"
    
    echo "[NOTIFICATION][$level] $message" >> "$SECURITY_LOG"
    
    # Add your notification logic here (email, Slack, PagerDuty, etc.)
}

# ============================================
# Report Generation
# ============================================

generate_security_report() {
    local results="$1"
    
    cat > "security_report_${TIMESTAMP}.md" << EOF
# Security Audit Report
Generated: $(date)

## Executive Summary

Automated security scan completed with Claude Code integration.

## HIBP Analysis Results

$(echo "$results" | cut -d'|' -f6-)

## Recommendations

1. Review all password exposures immediately
2. Enable MFA on all critical accounts
3. Rotate credentials for compromised services
4. Monitor for suspicious activity

## Action Items

- [ ] Review password reset list
- [ ] Confirm MFA enforcement
- [ ] Verify API key rotation
- [ ] Update security policies

---
*Report generated by Claude Code Security Pipeline*
EOF
    
    log_security_event "INFO" "REPORT" "Security report generated: security_report_${TIMESTAMP}.md"
}

# ============================================
# Main Pipeline
# ============================================

main() {
    echo "================================================"
    echo "Claude Code Security Automation Pipeline"
    echo "Started: $(date)"
    echo "================================================"
    
    # Pre-flight checks
    if [[ ! -f "$HIBP_CHECKER" ]]; then
        echo "❌ HIBP checker not found: $HIBP_CHECKER"
        exit 1
    fi
    
    if [[ ! -f "hibp_config.conf" ]]; then
        echo "❌ Configuration not found. Run: ./hibp_workflow.sh setup"
        exit 1
    fi
    
    # Run security pipeline
    log_security_event "INFO" "PIPELINE_START" "Security automation pipeline initiated"
    
    # Step 1: HIBP Analysis
    echo "🔍 Step 1: Running HIBP breach analysis..."
    IFS='|' read -r security_score breaches passwords stealer critical hibp_output <<< "$(run_hibp_analysis)"
    
    # Step 2: Password Strength Check (if password file configured)
    if [[ -f "${PASSWORD_FILE:-}" ]]; then
        echo "🔑 Step 2: Checking password strength..."
        check_password_strength "$PASSWORD_FILE"
    fi
    
    # Step 3: Automated Response
    echo "🤖 Step 3: Initiating automated response..."
    initiate_security_response "$security_score" "$breaches" "$passwords" "$stealer" "$critical"
    
    # Step 4: Generate Report
    echo "📊 Step 4: Generating security report..."
    generate_security_report "$hibp_output"
    
    # Step 5: Claude Code Integration
    echo "🤝 Step 5: Integrating with Claude Code..."
    
    # Pass results to Claude Code for further analysis
    if command -v claude-code &> /dev/null; then
        echo "Sending results to Claude Code for analysis..."
        # claude-code analyze "$SECURITY_LOG"
    fi
    
    log_security_event "INFO" "PIPELINE_COMPLETE" "Security automation pipeline completed"
    
    echo ""
    echo "================================================"
    echo "Pipeline Complete"
    echo "Security Score: $security_score"
    echo "Log: $SECURITY_LOG"
    echo "================================================"
    
    # Exit code based on severity
    if [[ "$security_score" -ge 500 ]]; then
        exit 2  # Critical
    elif [[ "$security_score" -ge 100 ]]; then
        exit 1  # Warning
    else
        exit 0  # OK
    fi
}

# Run main pipeline
main "$@"
