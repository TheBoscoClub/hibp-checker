# HIBP Dashboard

A local web dashboard for viewing Have I Been Pwned breach reports and monitoring logs.

## Features

- 📊 **Dashboard Statistics** - View total scans, breaches, and password exposures at a glance
- 📝 **Report Viewer** - Browse all breach reports with detailed information
- 🔍 **Full Report View** - Click any report to see complete breach details
- 📋 **Log Viewer** - View workflow, systemd, and error logs in real-time
- 🔄 **Auto-Refresh** - Dashboard automatically updates every 60 seconds
- ⬇️ **Download Reports** - Download any report for offline viewing
- 🎨 **Modern UI** - Clean, responsive interface with color-coded severity levels

## Quick Start

### Manual Start

```bash
cd ~/claude-archive/projects/hibp-project/dashboard
./start-dashboard.sh
```

Then open your browser to: http://127.0.0.1:5000

### Systemd Service (Automatic Start)

```bash
# Enable dashboard to start on boot
systemctl --user enable hibp-dashboard.service

# Start dashboard now
systemctl --user start hibp-dashboard.service

# Check status
systemctl --user status hibp-dashboard.service

# Stop dashboard
systemctl --user stop hibp-dashboard.service
```

## API Endpoints

The dashboard provides a REST API for programmatic access:

- `GET /` - Main dashboard interface
- `GET /api/stats` - Dashboard statistics
- `GET /api/reports` - List all breach reports
- `GET /api/report/<filename>` - Get detailed report
- `GET /api/logs/<type>` - Get log content (workflow, systemd, error)
- `GET /download/<filename>` - Download a report file

## Security

- Dashboard runs on **localhost only** (127.0.0.1) for security
- No external network access
- Read-only access to reports and logs
- Systemd hardening enabled (PrivateTmp, NoNewPrivileges)

## Requirements

- Python 3.6+
- Flask 2.0+ (automatically installed if missing)

## Logs

Dashboard logs are saved to:
- `~/.local/share/hibp-checker/dashboard.log` - Application log
- `~/.local/share/hibp-checker/dashboard.error.log` - Error log

## Troubleshooting

### Dashboard won't start

Check if port 5000 is already in use:
```bash
lsof -i :5000
```

### Can't access dashboard

Make sure you're accessing `http://127.0.0.1:5000` (not localhost or other IPs)

### Reports not showing

Verify reports exist in:
```bash
ls -lh ~/claude-archive/projects/hibp-project/reports/
```

## Customization

### Change Port

Edit `dashboard/app.py` and modify the last line:
```python
app.run(host='127.0.0.1', port=5000, debug=False)
```

### Change Refresh Interval

Edit `templates/index.html` and find:
```javascript
setInterval(() => {
    // ...
}, 60000);  // Change 60000 to desired milliseconds
```

## License

MIT License - Part of the HIBP Checker project
