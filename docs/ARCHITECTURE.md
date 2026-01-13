# Architecture

## Overview

HIBP Comprehensive Breach & Credential Stuffing Checker is a multi-component security tool built on the Have I Been Pwned API. It provides CLI tools, a web dashboard, automated scheduling, and Docker deployment options.

## System Context

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    HIBP Breach Checker                                   │
│                                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  ┌────────────┐ │
│  │  CLI Tools   │  │  Dashboard   │  │   Scheduling  │  │   Docker   │ │
│  │  (Python)    │  │   (Flask)    │  │   (systemd)   │  │  (Container)│ │
│  └──────┬───────┘  └──────┬───────┘  └───────┬───────┘  └─────┬──────┘ │
│         │                  │                  │                │        │
│         └──────────────────┼──────────────────┼────────────────┘        │
│                            │                  │                          │
│                   ┌────────▼──────────────────▼────────┐                │
│                   │         Core Libraries              │                │
│                   │  (hibp_comprehensive_checker.py)   │                │
│                   └────────────────┬───────────────────┘                │
│                                    │                                     │
└────────────────────────────────────┼─────────────────────────────────────┘
                                     │ HTTPS
                                     ▼
                          ┌─────────────────────┐
                          │   HIBP API v3       │
                          │ haveibeenpwned.com  │
                          └─────────────────────┘
```

## Component Architecture

### 1. Core Library

**hibp_comprehensive_checker.py**
- Main breach checking logic
- HIBP API client with rate limiting
- Multiple output formats (JSON, CSV, text)
- Stealer log analysis
- Password hash checking (k-anonymity)

### 2. CLI Tools

| Tool | Purpose |
|------|---------|
| `hibp_workflow.sh` | Main workflow orchestrator |
| `check-passwords.py` | Standalone password checker |
| `bw-hibp-stream.py` | Bitwarden streaming checker |
| `check-bitwarden-passwords.py` | Bitwarden vault checker |
| `multi_email_setup.sh` | Email list configuration |

### 3. Web Dashboard (Flask)

```
dashboard/
├── app.py                    # Flask application
├── bitwarden_checker.py      # Async Bitwarden checks
├── templates/
│   ├── index.html            # Main dashboard
│   └── archive.html          # Report archive
├── static/
│   ├── css/                  # Styles
│   └── js/                   # Frontend logic
├── systemd/
│   └── hibp-dashboard.service
├── start-dashboard.sh        # Linux launcher
├── start-dashboard.ps1       # Windows launcher
└── start-dashboard-macos.sh  # macOS launcher
```

**API Endpoints:**
- `GET /` - Dashboard UI
- `GET /api/stats` - Statistics
- `GET /api/reports` - Report listing
- `GET /api/report/<file>` - Report details
- `GET /api/logs/<type>` - Log viewer
- `POST /api/bitwarden/check` - Trigger Bitwarden scan
- `GET /api/bitwarden/task/<id>` - Check scan status

### 4. Scheduling Layer

**systemd Services:**
- `hibp-checker.service` - Main breach checker
- `hibp-checker.timer` - Scheduled execution
- `hibp-dashboard.service` - Dashboard auto-start

**Timer Features:**
- Configurable schedule (default: 2 AM daily)
- `OnBootSec=15min` - Run if missed during downtime
- Persistent timer state

### 5. Docker Layer

```
┌──────────────────────────────────────┐
│         Docker Compose               │
│                                      │
│  ┌─────────────┐  ┌──────────────┐  │
│  │   hibp      │  │  dashboard   │  │
│  │  (checker)  │  │   (Flask)    │  │
│  └──────┬──────┘  └──────┬───────┘  │
│         │                │          │
│         └────────┬───────┘          │
│                  │                  │
│         ┌────────▼────────┐         │
│         │  Shared Volume  │         │
│         │   (reports/)    │         │
│         └─────────────────┘         │
└──────────────────────────────────────┘
```

## Data Flow

### Breach Check Flow

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│ Email List  │────▶│  Workflow    │────▶│ HIBP API     │
│ (config)    │     │  Orchestrator│     │ (rate-limited)│
└─────────────┘     └──────┬───────┘     └──────┬───────┘
                           │                     │
                           ▼                     ▼
                    ┌─────────────┐       ┌─────────────┐
                    │ Local Report│◀──────│ API Response│
                    │ (JSON/CSV)  │       │ (breaches)  │
                    └──────┬──────┘       └─────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌─────────┐  ┌─────────┐  ┌─────────┐
        │Dashboard│  │ Systemd │  │  CLI    │
        │  (view) │  │ (notify)│  │ (exit)  │
        └─────────┘  └─────────┘  └─────────┘
```

### Password Check Flow (k-Anonymity)

```
Password: "MyPassword123"
         │
         ▼
┌─────────────────┐
│ SHA-1 Hash      │──▶ "8843D7F92416211DE9EBB963FF4CE28125932878"
└────────┬────────┘
         │
         ▼ Send only first 5 chars
┌─────────────────┐
│ HIBP Range API  │◀── "8843D" (k-anonymity)
└────────┬────────┘
         │
         ▼ Returns ~500 matching suffixes
┌─────────────────┐
│ Local Match     │──▶ Check if full hash in response
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Result: Found   │──▶ Breach count: 1,234,567
└─────────────────┘
```

## Directory Structure

```
hibp-project/
├── hibp_comprehensive_checker.py  # Core library
├── hibp_workflow.sh               # Main orchestrator
├── hibp_config.conf               # Configuration
├── bw-hibp-stream.py              # Bitwarden streamer
├── check-*.py                     # CLI tools
├── dashboard/                     # Flask web app
│   ├── app.py
│   ├── bitwarden_checker.py
│   ├── templates/
│   ├── static/
│   └── systemd/
├── scripts/                       # Setup scripts
│   ├── setup-systemd.sh
│   └── setup-cron.sh
├── tests/                         # pytest suite
│   ├── conftest.py
│   ├── test_*.py
│   └── fixtures/
├── reports/                       # Generated reports
├── logs/                          # Application logs
├── docker-compose.yml             # Docker orchestration
├── Dockerfile                     # Container image
├── docs/                          # Documentation
│   └── ARCHITECTURE.md            # This file
└── .github/
    └── workflows/
        ├── codeql.yml             # Security scanning
        └── security.yml           # Daily audits
```

## Security Architecture

### API Key Management

```
Priority Order:
1. Environment variable: $HIBP_API_KEY
2. Config file: hibp_config.conf
3. ~/.bw_session for Bitwarden

Best Practice:
export HIBP_API_KEY="..." in ~/.bashrc (never commit)
```

### Network Security

- Dashboard binds to 127.0.0.1 only
- All HIBP API calls use HTTPS
- Rate limiting prevents API abuse
- No external network listeners

### Data Security

- Passwords never stored in plaintext
- k-anonymity for password checks (only 5-char prefix sent)
- Reports contain breach data, not credentials
- Bitwarden streaming mode: passwords never touch disk

### systemd Hardening

```ini
ProtectSystem=strict
ProtectHome=read-only
NoNewPrivileges=true
PrivateTmp=true
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Core | Python 3.6+ | Main language |
| Web | Flask 2.0+ | Dashboard |
| HTTP | requests | API client |
| Scheduling | systemd | Linux automation |
| Container | Docker | Cross-platform |
| Testing | pytest | Test framework |
| Security | CodeQL, bandit | SAST scanning |

## API Dependencies

| Endpoint | Purpose | Auth Required |
|----------|---------|---------------|
| `/breachedaccount/{email}` | Email breaches | Yes |
| `/stealerlogsbyemail/{email}` | Stealer logs | Yes |
| `/pasteaccount/{email}` | Paste exposure | Yes |
| `/range/{hash_prefix}` | Password check | No |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | No breaches detected |
| 1 | Breaches found (non-critical) |
| 2 | Critical - passwords exposed or critical sites compromised |

## Scaling Considerations

| Subscription | RPM | Daily Capacity |
|--------------|-----|----------------|
| Pwned 1 | 10 | ~4,300 checks |
| Pwned 2 | 50 | ~21,600 checks |
| Pwned 3 | 100 | ~43,200 checks |
| Pwned 4 | 500 | ~216,000 checks |
