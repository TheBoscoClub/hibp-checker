# HIBP Dashboard Quick Reference

## 🎯 Access Your Dashboard

**Open in your browser:** http://127.0.0.1:5000

## 🚀 Dashboard Controls

### Start/Stop Dashboard

```bash
# Start dashboard
systemctl --user start hibp-dashboard.service

# Stop dashboard
systemctl --user stop hibp-dashboard.service

# Check if running
systemctl --user status hibp-dashboard.service

# Restart dashboard
systemctl --user restart hibp-dashboard.service
```

### Dashboard Features

#### 📊 Main Dashboard
- **Total Scans** - Number of HIBP scans performed
- **Total Breaches** - All breaches found across all emails
- **Password Exposures** - Critical count of exposed passwords
- **Stealer Logs** - Credential stuffing threats detected

#### 📝 Reports Tab
- View all breach reports chronologically
- Color-coded severity:
  - 🔴 **Critical** - Password exposures or critical sites compromised
  - 🟠 **Warning** - Breaches found but no password exposures
  - 🟢 **Clean** - No breaches detected
- Click any report to view full details
- Download reports for offline viewing

#### 📋 Logs Tab
- **Workflow Log** - Main HIBP checker workflow logs
- **Systemd Log** - System service execution logs
- **Error Log** - Error messages and debugging info
- Auto-scrolling log viewer
- Refresh button to update logs in real-time

## 🔧 Systemd Services Summary

### HIBP Checker (Automated Scanning)
```bash
# Next scheduled scan
systemctl --user list-timers hibp-checker.timer

# Run scan manually
systemctl --user start hibp-checker.service

# View scan logs
journalctl --user -u hibp-checker.service -f
```

### HIBP Dashboard (Web Interface)
```bash
# Dashboard status
systemctl --user status hibp-dashboard.service

# Dashboard logs
tail -f ~/.local/share/hibp-checker/dashboard.log
```

## 📁 File Locations

### Reports
- **Location:** `~/claude-archive/projects/hibp-project/reports/`
- **Format:** `hibp_report_YYYYMMDD_HHMMSS.txt`

### Logs
- **Workflow logs:** `~/claude-archive/projects/hibp-project/logs/`
- **Systemd logs:** `~/.local/share/hibp-checker/`
- **Dashboard logs:** `~/.local/share/hibp-checker/dashboard.log`

### Configuration
- **Main config:** `~/claude-archive/projects/hibp-project/hibp_config.conf`
- **API key:** `~/.config/hibp-checker/hibp-checker.env`
- **Email list:** `~/claude-archive/projects/hibp-project/my_emails.txt`

## 🔄 Automation Schedule

- **HIBP Checker:** Runs daily at ~3:00 AM (±30 min randomization)
- **Dashboard:** Runs continuously, auto-refreshes every 60 seconds
- **Next scan:** Check with `systemctl --user list-timers hibp-checker.timer`

## 🔐 Security Notes

- Dashboard is **localhost-only** (127.0.0.1) - not accessible from network
- All data stays on your local machine
- API key stored with 600 permissions
- No external data transmission (except HIBP API calls)

## 🐛 Troubleshooting

### Dashboard not accessible
```bash
# Check if service is running
systemctl --user status hibp-dashboard.service

# Check if port 5000 is in use
lsof -i :5000

# Restart dashboard
systemctl --user restart hibp-dashboard.service
```

### No reports showing
```bash
# Verify reports exist
ls -lh ~/claude-archive/projects/hibp-project/reports/

# Run manual scan
systemctl --user start hibp-checker.service
```

### API key errors
```bash
# Check API key is set
cat ~/.config/hibp-checker/hibp-checker.env

# Test API key manually
python3 ~/claude-archive/projects/hibp-project/hibp_comprehensive_checker.py \
    -k $(grep HIBP_API_KEY ~/.config/hibp-checker/hibp-checker.env | cut -d= -f2) \
    -e test@example.com -o text
```

## 📱 Mobile Access

While the dashboard is localhost-only, you can:
1. Set up SSH tunnel from your phone
2. Access via `http://127.0.0.1:5000` through the tunnel
3. Responsive design works on mobile browsers

## 🎨 Dashboard Customization

To change the refresh interval, edit:
`~/claude-archive/projects/hibp-project/dashboard/templates/index.html`

Find the line:
```javascript
setInterval(() => { ... }, 60000);  // 60000 = 60 seconds
```

To change the port, edit:
`~/claude-archive/projects/hibp-project/dashboard/app.py`

Change:
```python
app.run(host='127.0.0.1', port=5000, debug=False)
```

## 📧 Email Notifications

Email notifications are sent to: **gjbr@pm.me**

Notification settings in `hibp_config.conf`:
- `SEND_NOTIFICATIONS=true` - Enabled
- `NOTIFICATION_EMAIL="gjbr@pm.me"` - Recipient
- `NOTIFY_ONLY_NEW=true` - Only new breaches

---

**Need Help?** Check the main README at `~/claude-archive/projects/hibp-project/README.md`
