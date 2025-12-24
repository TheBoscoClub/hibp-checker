# Release Notes - v2.0.1

**Release Date**: November 24, 2025
**Type**: Patch Release
**Focus**: Systemd improvements, utility scripts, and bug fixes

---

## 🎯 Overview

Version 2.0.1 is a patch release that improves the systemd timer configuration, adds utility scripts for password checking, and fixes path issues in the systemd service templates.

---

## ✨ What's New

### Utility Scripts

Four new utility scripts have been added to enhance functionality:

- **`check-bitwarden-passwords.py`** - Direct integration with Bitwarden vault for password breach checking
- **`check-passwords.py`** - Standalone password breach checker without email checking
- **`verify-dns.sh`** - DNS verification utility for troubleshooting network issues
- **`launch-dashboard.sh`** - Quick launcher script for the web dashboard

### Dashboard Enhancements

- Added archive template (`dashboard/templates/archive.html`) for viewing historical breach reports

---

## 🔧 Improvements

### Systemd Timer Configuration

The systemd timer has been significantly improved for better reliability:

- **Schedule Change**: Default run time changed from 3 AM to 2 AM
- **Boot Recovery**: Added `OnBootSec=15min` - automatically runs 15 minutes after boot if the scheduled time was missed (e.g., computer was off at 2 AM)
- **Path Corrections**: Updated all systemd paths from `~/claude-archive/projects/hibp-project` to `/raid0/ClaudeCodeProjects/hibp-project`

These changes ensure the checker runs reliably even if your system isn't powered on 24/7.

### Project Management

- Enhanced `.gitignore` to properly exclude release artifacts
- Removed release archives from version control

---

## 🐛 Bug Fixes

- **Fixed systemd service paths**: Corrected `WorkingDirectory` and `ExecStart` paths in service template
- **Fixed ReadWritePaths**: Updated to reference correct project directory
- **Improved timer resilience**: Better handling of system downtime and missed schedules

---

## 📚 Documentation

### New Documentation

- `DOCKER_PUBLISH_INSTRUCTIONS.md` - Complete workflow for publishing Docker images to GHCR
- `GITHUB_RELEASE_INSTRUCTIONS.md` - Step-by-step guide for creating GitHub releases

---

## 📦 Installation

### Upgrade from v2.0.0

```bash
cd /path/to/hibp-checker
git pull origin main
git checkout v2.0.1

# Update systemd services (if using systemd)
cp systemd/hibp-checker.timer ~/.config/systemd/user/
cp systemd/hibp-checker.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user restart hibp-checker.timer
```

### Fresh Installation

```bash
# Clone repository
git clone https://github.com/greogory/hibp-checker.git
cd hibp-checker
git checkout v2.0.1

# Run quick start
./quick_start.sh
```

### Docker

```bash
# Pull latest image
docker pull ghcr.io/greogory/hibp-checker:2.0.1

# Or use latest tag
docker pull ghcr.io/greogory/hibp-checker:latest
```

---

## 🔍 What's Changed

### Files Modified
- `.gitignore` - Added release artifact patterns
- `CHANGELOG.md` - Added v2.0.1 release notes
- `VERSION` - Bumped to 2.0.1
- `systemd/hibp-checker.timer` - Improved scheduling
- `systemd/hibp-checker.service` - Fixed paths
- `dashboard/app.py` - Minor enhancements
- `dashboard/templates/index.html` - UI improvements

### Files Added
- `check-bitwarden-passwords.py` - Bitwarden integration
- `check-passwords.py` - Password checker utility
- `verify-dns.sh` - DNS verification tool
- `launch-dashboard.sh` - Dashboard launcher
- `dashboard/templates/archive.html` - Archive template
- `DOCKER_PUBLISH_INSTRUCTIONS.md` - Docker docs
- `GITHUB_RELEASE_INSTRUCTIONS.md` - Release docs
- `RELEASE_NOTES_v2.0.1.md` - This file

---

## 🐳 Docker Images

Docker images for this release are available at:

```
ghcr.io/greogory/hibp-checker:2.0.1
ghcr.io/greogory/hibp-checker:latest
```

**Image Details**:
- Base: `python:3.11-slim`
- Size: ~143 MB
- Platforms: `linux/amd64`
- Includes: Dashboard, all utilities, Flask

---

## 📊 Release Statistics

- **Commits**: 1
- **Files Changed**: 14
- **Lines Added**: 1,482
- **Lines Removed**: 32
- **New Scripts**: 4
- **Documentation**: 2 new guides

---

## 🔒 Security

No security vulnerabilities were fixed in this release. All security features from v2.0.0 remain intact.

---

## 🙏 Acknowledgments

- **Troy Hunt** for maintaining [Have I Been Pwned](https://haveibeenpwned.com)
- All users who provided feedback on systemd timer behavior

---

## 📝 Full Changelog

**Full Changelog**: https://github.com/greogory/hibp-checker/compare/v2.0.0...v2.0.1

---

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/greogory/hibp-checker/issues)
- **Documentation**: [README.md](README.md)
- **Dashboard Guide**: [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)
- **Email**: gjbr@pm.me

---

**Checksums (SHA256)**:
```
3e09787bf5cfbd5cd6f71aa8b88903e3adf0cd069a90ac91d0a5c4a932308b40  hibp-checker-v2.0.1.tar.gz
dd52c7725d589ff738ea2362a44e433e21c8493ec6a457220b396689294e7862  hibp-checker-v2.0.1.zip
```
