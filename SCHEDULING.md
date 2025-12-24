# ⏰ HIBP Checker - Automated Scheduling Guide

## ⚡ Powered by Have I Been Pwned

**This tool is built on top of the [Have I Been Pwned](https://haveibeenpwned.com) service created by Troy Hunt.**

### 📜 Attribution & Licensing
This project uses data from **Have I Been Pwned**, licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

### ⚠️ Prerequisites - HIBP API Key Required
**MANDATORY REQUIREMENT**: This tool requires a **Have I Been Pwned API subscription** (Pwned 1-4 tier) to function.

- 🔑 **Get API Key**: [HIBP API Key](https://haveibeenpwned.com/API/Key)
- 📚 **API Documentation**: [HIBP API v3](https://haveibeenpwned.com/API/v3)
- 💝 **Support HIBP**: [Donate](https://haveibeenpwned.com/Donate)

---

## Overview

This guide covers three methods for scheduling automated HIBP checks:

1. **Systemd Timers** (Linux with systemd) - Recommended for most Linux users
2. **Cron Jobs** (Linux/macOS without systemd) - Universal Unix/Linux solution
3. **Docker Compose with Ofelia** (Cross-platform) - Best for containerized environments

Choose the method that best fits your environment.

---

## Method 1: Systemd Timers (Linux)

### Features
- ✅ Native Linux integration
- ✅ Automatic retry on failure
- ✅ Persistent scheduling (runs missed jobs after boot)
- ✅ Randomized delays to avoid API rate limits
- ✅ Easy log management with journalctl
- ✅ Security hardening with systemd directives

### Prerequisites
- Systemd-based Linux distribution (most modern distros)
- User-level systemd support

### Quick Setup

```bash
cd <project-directory>
./scripts/setup-systemd.sh
```

The script will:
1. Create necessary directories
2. Prompt for API key configuration (if not set)
3. Install systemd service and timer units
4. Offer choice of daily, weekly, or both schedules
5. Enable and start the selected timers

### Available Timers

#### Daily Timer
- **Schedule**: Every day at 3:00 AM
- **Randomization**: ±30 minutes (2:30 AM - 3:30 AM)
- **Use case**: Active monitoring, frequent breach checks

```bash
# Enable daily timer
systemctl --user enable --now hibp-checker.timer
```

#### Weekly Timer
- **Schedule**: Every Monday at 9:00 AM
- **Randomization**: ±1 hour (8:00 AM - 10:00 AM)
- **Use case**: Periodic checks, lower API usage

```bash
# Enable weekly timer
systemctl --user enable --now hibp-checker-weekly.timer
```

### Management Commands

```bash
# View timer status
systemctl --user status hibp-checker.timer

# List all active timers
systemctl --user list-timers

# View service logs
journalctl --user -u hibp-checker.service -f

# Run check manually (immediate)
systemctl --user start hibp-checker.service

# Stop timer
systemctl --user stop hibp-checker.timer

# Disable timer (prevent auto-start on boot)
systemctl --user disable hibp-checker.timer

# View next scheduled run
systemctl --user list-timers hibp-checker.timer
```

### Log Files

Logs are saved to `~/.local/share/hibp-checker/`:
- `hibp-checker.log` - Standard output
- `hibp-checker.error.log` - Error output

```bash
# View logs
tail -f ~/.local/share/hibp-checker/hibp-checker.log
tail -f ~/.local/share/hibp-checker/hibp-checker.error.log
```

### Security Features

The systemd service includes hardening directives:
- `PrivateTmp=yes` - Private /tmp directory
- `NoNewPrivileges=yes` - Prevent privilege escalation
- `ProtectSystem=strict` - Read-only system directories
- `ProtectHome=read-only` - Read-only home directory
- `ReadWritePaths` - Limited write access to logs/reports only

### Customization

To modify the schedule, edit the timer files:

```bash
# Edit daily timer
systemctl --user edit hibp-checker.timer

# Example: Change to 2 AM
[Timer]
OnCalendar=*-*-* 02:00:00
```

After editing, reload systemd:

```bash
systemctl --user daemon-reload
systemctl --user restart hibp-checker.timer
```

---

## Method 2: Cron Jobs (Linux/macOS)

### Features
- ✅ Universal Unix/Linux compatibility
- ✅ Works on systems without systemd
- ✅ Simple, well-understood scheduling
- ✅ Lightweight

### Prerequisites
- Cron daemon installed (usually pre-installed)
- Bash shell

### Quick Setup

```bash
cd <project-directory>
./scripts/setup-cron.sh
```

The script will:
1. Create necessary directories
2. Prompt for API key configuration (if not set)
3. Create a wrapper script for cron
4. Offer schedule choices or custom cron syntax
5. Install the cron job

### Schedule Options

The setup script offers:
1. **Daily at 3 AM**: `0 3 * * *`
2. **Weekly on Monday at 9 AM**: `0 9 * * 1`
3. **Custom**: Enter your own cron syntax

### Cron Syntax Reference

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
│ │ │ │ │
│ │ │ │ │
* * * * * command
```

**Common Examples**:
- `0 3 * * *` - Daily at 3:00 AM
- `0 9 * * 1` - Every Monday at 9:00 AM
- `0 */6 * * *` - Every 6 hours
- `30 2 1 * *` - First day of month at 2:30 AM
- `0 0 * * 0` - Every Sunday at midnight

### Management Commands

```bash
# List all cron jobs
crontab -l

# Edit cron jobs
crontab -e

# Remove all cron jobs (careful!)
crontab -r

# View cron logs (varies by system)
# Linux with systemd:
journalctl -u cron -f

# macOS:
tail -f /var/log/system.log | grep cron

# Traditional Linux:
tail -f /var/log/cron
```

### Log Files

Logs are saved to `~/.local/share/hibp-checker/`:
- `hibp-checker.log` - Standard output
- `hibp-checker.error.log` - Error output

```bash
# View logs
tail -f ~/.local/share/hibp-checker/hibp-checker.log
tail -f ~/.local/share/hibp-checker/hibp-checker.error.log
```

### Manual Test

Test the cron wrapper script manually:

```bash
<project-directory>/scripts/hibp-cron-wrapper.sh
```

### Troubleshooting

**Cron job not running?**
1. Check cron daemon is running:
   ```bash
   # Linux
   sudo systemctl status cron
   # or
   sudo systemctl status crond

   # macOS
   sudo launchctl list | grep cron
   ```

2. Check cron logs for errors (see Management Commands above)

3. Verify the wrapper script is executable:
   ```bash
   ls -l <project-directory>/scripts/hibp-cron-wrapper.sh
   ```

4. Test the wrapper script manually to check for errors

**Environment variables not working?**
- Cron runs with a minimal environment
- The wrapper script sources `~/.config/hibp-checker/hibp-checker.env`
- Make sure your API key is saved there

---

## Method 3: Docker Compose with Ofelia (Cross-Platform)

### Features
- ✅ Works on Windows, macOS, and Linux
- ✅ Containerized scheduling
- ✅ No host system dependencies
- ✅ Easy to deploy and manage
- ✅ Portable configuration

### Prerequisites
- Docker Engine 20.10+
- Docker Compose v2.0+

### Quick Setup

1. **Create environment file**:
   ```bash
   echo "HIBP_API_KEY=your-api-key-here" > .env
   ```

2. **Create email list**:
   ```bash
   cp my_emails_template.txt my_emails.txt
   # Edit my_emails.txt with your email addresses
   ```

3. **Start scheduled service**:
   ```bash
   docker compose -f docker-compose.scheduled.yml up -d
   ```

### Configuration

The `docker-compose.scheduled.yml` uses [Ofelia](https://github.com/mcuadros/ofelia), a modern job scheduler for Docker.

**Default schedules**:
- **Daily**: 3:00 AM every day
- **Weekly** (optional profile): 9:00 AM every Monday

### Schedule Customization

Edit `docker-compose.scheduled.yml` to change schedules:

```yaml
labels:
  # Daily at 3 AM
  ofelia.job-exec.hibp-daily.schedule: "0 3 * * *"

  # Change to 2 AM:
  ofelia.job-exec.hibp-daily.schedule: "0 2 * * *"

  # Every 12 hours:
  ofelia.job-exec.hibp-daily.schedule: "0 */12 * * *"
```

### Management Commands

```bash
# Start scheduled service
docker compose -f docker-compose.scheduled.yml up -d

# Start with weekly profile too
docker compose -f docker-compose.scheduled.yml --profile weekly up -d

# View logs
docker compose -f docker-compose.scheduled.yml logs -f

# View scheduler logs only
docker logs -f hibp-scheduler

# View worker logs only
docker logs -f hibp-worker

# Stop scheduled service
docker compose -f docker-compose.scheduled.yml down

# Restart service
docker compose -f docker-compose.scheduled.yml restart

# Trigger manual check immediately
docker exec hibp-worker python3 hibp_comprehensive_checker.py --email-file /app/data/my_emails.txt -o text -v
```

### Platform-Specific Examples

#### Windows (PowerShell)
```powershell
# Set API key
$env:HIBP_API_KEY="your-api-key-here"

# Start scheduler
docker compose -f docker-compose.scheduled.yml up -d

# View logs
docker compose -f docker-compose.scheduled.yml logs -f
```

#### Windows (CMD)
```cmd
# Set API key
set HIBP_API_KEY=your-api-key-here

# Start scheduler
docker compose -f docker-compose.scheduled.yml up -d

# View logs
docker compose -f docker-compose.scheduled.yml logs -f
```

#### macOS/Linux
```bash
# Set API key in .env file
echo "HIBP_API_KEY=your-api-key-here" > .env

# Start scheduler
docker compose -f docker-compose.scheduled.yml up -d

# View logs
docker compose -f docker-compose.scheduled.yml logs -f
```

### Log Files

Logs are saved to the host in `./logs/`:
- `hibp-checker.log` - Standard output
- `hibp-checker.error.log` - Error output

```bash
# View logs (host filesystem)
tail -f logs/hibp-checker.log
tail -f logs/hibp-checker.error.log

# View container logs (Docker)
docker logs -f hibp-worker
```

### Volume Mounts

The scheduler mounts:
- `./my_emails.txt` → `/app/data/my_emails.txt` (read-only)
- `./reports` → `/app/reports` (read-write)
- `./logs` → `/app/logs` (read-write)

Reports and logs persist on the host filesystem.

### Troubleshooting

**Scheduler not running jobs?**
1. Check Ofelia logs:
   ```bash
   docker logs hibp-scheduler
   ```

2. Verify time zone:
   ```bash
   docker exec hibp-scheduler date
   ```

   If needed, add timezone to scheduler:
   ```yaml
   hibp-scheduler:
     environment:
       - TZ=America/New_York
   ```

3. Check worker is running:
   ```bash
   docker ps | grep hibp-worker
   ```

**API key not working?**
1. Check environment variable:
   ```bash
   docker exec hibp-worker env | grep HIBP_API_KEY
   ```

2. Verify .env file exists and has correct format:
   ```bash
   cat .env
   # Should show: HIBP_API_KEY=your-key
   ```

3. Restart containers after changing .env:
   ```bash
   docker compose -f docker-compose.scheduled.yml down
   docker compose -f docker-compose.scheduled.yml up -d
   ```

---

## Comparison Matrix

| Feature | Systemd | Cron | Docker |
|---------|---------|------|--------|
| **Platform** | Linux only | Linux/macOS | All platforms |
| **Setup complexity** | Low | Low | Medium |
| **Resource usage** | Very low | Very low | Low-Medium |
| **Persistent jobs** | ✅ Yes | ❌ No | ✅ Yes |
| **Easy logging** | ✅ journalctl | ⚠️ Manual | ✅ Docker logs |
| **Security hardening** | ✅ Built-in | ⚠️ Manual | ✅ Containers |
| **Randomization** | ✅ Built-in | ❌ No | ❌ No |
| **Dependencies** | Systemd | Cron | Docker |
| **Portability** | Low | Medium | High |

---

## Recommended Setup

Choose based on your environment:

### Linux Desktop/Server with Systemd
→ **Use Systemd Timers**
- Best integration with system
- Automatic retry and persistence
- Built-in randomization
- Easy log management

### Linux/macOS without Systemd
→ **Use Cron**
- Universal compatibility
- Simple and reliable
- Well-understood

### Windows, Multi-platform, or Containerized
→ **Use Docker Compose**
- Works everywhere
- Self-contained
- Easy to deploy and move

### Development/Testing
→ **Manual execution**
```bash
# Direct Python
python3 hibp_comprehensive_checker.py -e you@example.com

# Via workflow script
./hibp_workflow.sh check

# Via Docker
docker run --rm -e HIBP_API_KEY=your-key \
  ghcr.io/greogory/hibp-checker:latest \
  python3 hibp_comprehensive_checker.py -e you@example.com
```

---

## Best Practices

### 1. API Rate Limiting
- Don't schedule too frequently (minimum: daily)
- Use randomization to spread load (systemd does this automatically)
- Monitor your API usage at https://haveibeenpwned.com/API/Key

### 2. Log Management
- Regularly check logs for errors
- Set up log rotation:
  ```bash
  # Linux with logrotate
  sudo nano /etc/logrotate.d/hibp-checker
  ```

  Content:
  ```
  /home/*/.local/share/hibp-checker/*.log {
      weekly
      rotate 4
      compress
      missingok
      notifempty
  }
  ```

### 3. Email List Maintenance
- Keep `my_emails.txt` updated
- Remove old/unused addresses
- Add new addresses as needed

### 4. Report Review
- Check reports regularly in `./reports/`
- Set up notifications for new breaches (future feature)
- Archive old reports periodically

### 5. Security
- **Never commit API keys to Git**
- Store API key in secure location:
  - Systemd/Cron: `~/.config/hibp-checker/hibp-checker.env`
  - Docker: `.env` file (add to `.gitignore`)
- Restrict file permissions:
  ```bash
  chmod 600 ~/.config/hibp-checker/hibp-checker.env
  chmod 600 .env
  ```

### 6. Monitoring
Set up basic monitoring:

```bash
# Check last run time (systemd)
systemctl --user status hibp-checker.timer

# Check last run time (cron)
ls -lh ~/.local/share/hibp-checker/hibp-checker.log

# Check last run time (Docker)
docker logs --tail 50 hibp-worker
```

---

## Troubleshooting Common Issues

### API Key Not Found
**Symptoms**: "HIBP_API_KEY environment variable not set"

**Solutions**:
- Systemd: Check `~/.config/hibp-checker/hibp-checker.env` exists and is readable
- Cron: Same as systemd
- Docker: Check `.env` file in project directory

### Permission Denied
**Symptoms**: Cannot write to logs or reports

**Solutions**:
```bash
# Fix ownership
chown -R $USER:$USER <project-directory>/

# Fix permissions
chmod -R u+rwX <project-directory>/
```

### Jobs Not Running
**Symptoms**: No new logs, reports not updating

**Solutions**:
- **Systemd**: Check timer is active: `systemctl --user list-timers`
- **Cron**: Check crontab: `crontab -l`
- **Docker**: Check containers running: `docker ps`

### Network Errors
**Symptoms**: API connection failures

**Solutions**:
1. Check internet connection
2. Verify HIBP API is accessible:
   ```bash
   curl -I https://haveibeenpwned.com
   ```
3. Check firewall rules
4. Verify API key is valid at https://haveibeenpwned.com/API/Key

---

## Advanced Configurations

### Multiple Email Lists
Run separate checks for different email lists:

#### Systemd
Create separate service/timer files:
```bash
cp systemd/hibp-checker.service systemd/hibp-checker-personal.service
cp systemd/hibp-checker.timer systemd/hibp-checker-personal.timer

# Edit service to use different email file
```

#### Cron
Add multiple cron entries:
```cron
0 3 * * * /path/to/wrapper.sh --email-file personal_emails.txt
0 4 * * * /path/to/wrapper.sh --email-file work_emails.txt
```

#### Docker
Add multiple worker services in `docker-compose.scheduled.yml`

### Different Schedules Per Email List
Useful for high-priority vs. low-priority monitoring:

```yaml
# High-priority emails: daily
ofelia.job-exec.hibp-critical.schedule: "0 3 * * *"

# Normal emails: weekly
ofelia.job-exec.hibp-normal.schedule: "0 9 * * 1"

# Old accounts: monthly
ofelia.job-exec.hibp-archive.schedule: "0 9 1 * *"
```

### Notification Integration
Add notification commands to wrapper scripts:

```bash
#!/bin/bash
# Run check
./hibp_workflow.sh check

# Send notification if breaches found
if grep -q "BREACHED" reports/latest_report.txt; then
    # Send email
    mail -s "HIBP Alert: New Breach Found" you@example.com < reports/latest_report.txt

    # Or use ntfy
    curl -d "New breach detected!" ntfy.sh/your-topic
fi
```

---

## Support

For issues or questions:
- 📁 **Project Issues**: https://github.com/greogory/hibp-checker/issues
- 📚 **HIBP API Docs**: https://haveibeenpwned.com/API/v3
- 💬 **HIBP Support**: https://haveibeenpwned.com/About

---

## License

This scheduling documentation is part of the HIBP Checker project.

**Data License**: All breach data from Have I Been Pwned is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

**Project License**: MIT License (see LICENSE file)
