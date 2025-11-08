# HIBP Checker v2.0.0 - Dashboard Release

**Release Date:** November 7, 2025

## 🎉 Introducing the Web Dashboard!

We're excited to announce HIBP Checker v2.0.0, featuring a brand new **web-based dashboard** for viewing your breach reports and monitoring logs through a modern, user-friendly interface!

![Dashboard Preview](https://via.placeholder.com/800x400?text=HIBP+Dashboard+v2.0)

## ✨ What's New

### 📊 Web Dashboard

The star of this release is the new web dashboard that provides:

- **Real-time Statistics** - See total scans, breaches, and password exposures at a glance
- **Report Browser** - Browse all your breach reports with color-coded severity
- **Full Report Viewer** - Click any report to see complete breach details
- **Log Monitoring** - View workflow, systemd, and error logs in real-time
- **Auto-Refresh** - Dashboard updates automatically every 60 seconds
- **Download Reports** - Export any report for offline viewing
- **Mobile-Friendly** - Responsive design works on all devices

### 🌍 Cross-Platform Support

The dashboard works seamlessly across all platforms:

- **Linux** - Native Flask application with systemd integration
- **Windows** - Docker-based deployment with PowerShell scripts
- **macOS** - Docker or native installation with bash scripts

## 🚀 Quick Start

### Linux

```bash
# Start dashboard
cd dashboard
./start-dashboard.sh

# Or use systemd (auto-starts on boot)
systemctl --user enable --now hibp-dashboard.service

# Access at http://127.0.0.1:5000
```

### Windows

```powershell
# Using Docker (recommended)
docker-compose --profile dashboard up -d

# Or native PowerShell
cd dashboard
.\start-dashboard.ps1

# Access at http://127.0.0.1:5000
```

### macOS

```bash
# Using Docker (recommended)
docker-compose --profile dashboard up -d

# Or native installation
cd dashboard
./start-dashboard-macos.sh

# Access at http://127.0.0.1:5000
```

## 📖 Documentation

We've added comprehensive documentation for the dashboard:

- **[Dashboard Guide](DASHBOARD_GUIDE.md)** - Quick reference for using the dashboard
- **[Dashboard README](dashboard/README.md)** - Detailed setup and API documentation
- **[Changelog](CHANGELOG.md)** - Complete list of changes

## 🔧 Technical Details

### New Components

- Flask-based REST API backend
- Single-page HTML/CSS/JS frontend
- Systemd service for Linux
- Docker Compose profile for containerized deployment
- Cross-platform startup scripts

### Dependencies

- Flask >= 2.0.0 (new)
- requests >= 2.25.0 (existing)

Install with:
```bash
pip install -r requirements.txt
```

### API Endpoints

The dashboard provides a REST API:

- `GET /api/stats` - Dashboard statistics
- `GET /api/reports` - List all reports
- `GET /api/report/<filename>` - Report details
- `GET /api/logs/<type>` - Log content
- `GET /download/<filename>` - Download reports

## 🔐 Security

- Dashboard runs on **localhost only** (127.0.0.1) for security
- No external network access
- Read-only access to reports and logs
- Systemd hardening enabled on Linux

## 📦 Upgrading from v1.x

Upgrading is simple and non-breaking:

```bash
# Pull latest code
git pull

# Install new dependencies
pip install -r requirements.txt

# Start dashboard
cd dashboard
./start-dashboard.sh
```

**All existing functionality remains unchanged!** The dashboard is purely additive.

## 🐳 Docker Updates

Docker users can pull the new image:

```bash
# Update image
docker-compose pull

# Start with dashboard
docker-compose --profile dashboard up -d
```

The new image includes:
- Dashboard application
- Flask web server
- All cross-platform scripts

## 🎯 Use Cases

The dashboard is perfect for:

- **Quick Breach Review** - Instantly see which emails have breaches
- **Monitoring** - Track new scans and their results
- **Debugging** - View logs without SSH or terminal access
- **Reporting** - Download and share breach reports
- **Historical Analysis** - Browse all past scans

## 🛠️ What Hasn't Changed

All existing features work exactly as before:

- ✅ Command-line breach checking
- ✅ Automated scheduling
- ✅ Email notifications
- ✅ Multi-format reports
- ✅ Stealer log detection
- ✅ Password checking
- ✅ Docker support

## 📝 Known Issues

None at this time. If you encounter any issues, please report them on our [GitHub Issues](https://github.com/greogory/hibp-checker/issues) page.

## 🙏 Acknowledgments

- **Troy Hunt** for creating and maintaining Have I Been Pwned
- The HIBP community for their continued support
- All contributors who helped test the dashboard

## 📣 What's Next

Planned for future releases:

- Email notification controls in dashboard
- Breach timeline visualization
- Comparison between scans
- Export options (PDF, Excel)
- Custom alert thresholds

## 🔗 Links

- **Documentation**: [README.md](README.md)
- **Dashboard Guide**: [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)
- **Docker Guide**: [DOCKER.md](DOCKER.md)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **GitHub**: https://github.com/greogory/hibp-checker
- **Have I Been Pwned**: https://haveibeenpwned.com

---

**Download:** [hibp-checker-v2.0.0.tar.gz](https://github.com/greogory/hibp-checker/releases/tag/v2.0.0)

**Docker Image:** `ghcr.io/greogory/hibp-checker:2.0.0` or `ghcr.io/greogory/hibp-checker:latest`

---

Thank you for using HIBP Checker! We hope you enjoy the new dashboard. 🎉

If you find this tool useful, please consider:
- ⭐ Star the repository on GitHub
- 💝 Support HIBP with a [subscription](https://haveibeenpwned.com/API/Key) or [donation](https://haveibeenpwned.com/Donate)
- 🐛 Report bugs or suggest features via GitHub Issues
- 📢 Share with others who might benefit from breach monitoring
