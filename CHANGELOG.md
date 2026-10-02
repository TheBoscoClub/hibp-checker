# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Semgrep CI workflow** (`.github/workflows/semgrep.yml`): runs `semgrep ci` — Code (SAST), Secrets and Supply Chain — diff-aware on pull requests, full on pushes to `main`, weekly on schedule and on manual dispatch, reporting to the Semgrep AppSec Platform (deployment `gjbr-pm-me`). Engine image pinned `tag@digest`; the sole credential is the Agent (CI) scoped `SEMGREP_APP_TOKEN` org secret — no GitHub App is installed and Semgrep is granted no code access

### Changed

- **Dependabot auto-merge waits for the PR's checks** (`.github/workflows/dependabot-auto-merge.yml`): `main` has no required status checks, so `gh pr merge --auto` merged the instant it ran — #35 landed while its Ruff and pytest checks were still running. The job now polls every other check on the PR head (excluding itself) until none is pending and `Python Tests` has passed, fails on any failed or cancelled check, and gives up after 30 minutes
- **Explicit ruff rule selection** (`ruff.toml`): ruff 0.16 grew its default rule set from 59 to 413 rules, which turned the `ruff-action` v4 bump into 117 findings in unchanged code. Rules are now selected explicitly — `E`, `F`, `W` with `E501` ignored — so a ruff release can no longer change what CI enforces. The gitignored local `pyproject.toml` carried that same selection in a `[tool.ruff]` table that `ruff.toml` has always shadowed; it was dead config and is gone
- **Test dependency minimums** (`requirements.txt`): `pytest>=9.0.3`, `pytest-mock>=3.16.0`, `responses>=0.26.0` (Dependabot #32, #35, #34)
- **GitHub Actions pins**: `actions/upload-artifact` 7.0.1, `docker/login-action` 4.1.0, `docker/build-push-action` 7.1.0, `astral-sh/ruff-action` 4.0.0 (Dependabot #29, #27, #30, #31)

### Fixed

- **Codecov upload failed on every push to `main`** (`.github/workflows/ci.yml`): the action's wrapper verifies the CLI download against a signing key fetched from keybase, and Codecov deleted the `codecovsecurity` keybase account that v5 and v6 fetch it from — the import got a 404 (`gpg: no valid OpenPGP data found`) and the wrapper exited with `Could not verify signature`. `codecov/codecov-action` is now v7.1.1, which fetches the same key from the replacement `codecovsecops` account. Dependabot's v6.0.0 bump (#26) was merged first and was not enough on its own

### Security

- **Exception text no longer returned by `/api/bitwarden/status`** (`dashboard/bitwarden_checker.py` `check_prerequisites`): an unexpected failure of `bw status` appended `str(e)` to the `errors` list that the endpoint returns verbatim, so filesystem paths and OS error strings could reach the browser (CodeQL `py/stack-trace-exposure`, alert #76). The response now carries a fixed message and the detail goes to the server log
- **Report lookup proves containment** (`dashboard/bitwarden_checker.py` `get_report_by_filename`): the basename-only sanitisation is kept, and the resolved path must now also be a regular `.json` file whose parent is the resolved reports directory, so a symlink planted in the directory cannot point outside it (CodeQL `py/path-injection`, alerts #77 and #78)
- **API key no longer passed on the command line** (`hibp_comprehensive_checker.py` `-k/--api-key`, `hibp_workflow.sh` `run_checker`): the key was interpolated into the process argv, where `ps` exposes it to every user on the host and where crash artifacts and process listings capture it. `-k` now defaults to `$HIBP_API_KEY` and is no longer `required=True`, with an explicit post-parse check so a missing key fails as "no key supplied" rather than reaching the API and returning a 401 that reads like "bad key". `-k` is still accepted for compatibility
- **Key read from the canonical credential store on demand** (`hibp_workflow.sh` `read_key_from_canonical_store`/`load_config`, `quick_start.sh`): no script sourced `~/.config/api-keys.env` — all of them relied on `HIBP_API_KEY` being ambient in the environment. That is precisely *why* it was exported from `~/.config/environment.d`, which injects into the systemd user manager and therefore the entire graphical session; `plasmashell` and `kwin_wayland` were both measured carrying it. The store is now sourced in a **subshell** that prints back only this one value, so the other credentials it holds never enter the process environment
- **Key no longer written into `hibp_config.conf`** (`quick_start.sh`, generated config template): both the setup heredoc and a `sed -i` wrote it there, creating a second source of truth that goes stale at the next rotation while still looking valid. Precedence is now environment > canonical store > config file, so a key left in an older config still works but warns
  - **Verified in both directions against the real process**: `new form: dummy_in_cmdline=0, key_in_environ=1` / `old form: dummy_in_cmdline=1`. The first attempt at this test measured the backgrounded wrapper shell rather than the `python3` child and was silently meaningless in *both* directions — the control returning 0 is what exposed it. Retrieval proven under `env -i`: 0 credential names before, key obtained, 0 after

- **`requests` upgrade to 2.33.1**: Bumped from `2.32.5` in `requirements.txt` to address [GHSA-gc5v-m9x4-r6x2](https://github.com/advisories/GHSA-gc5v-m9x4-r6x2) — insecure temp file reuse in `requests.utils.extract_zipped_paths()` (CVSS 4.4, medium). The vulnerable utility is not invoked by this project (HIBP client uses HTTPS only, no zip extraction), but the dependency is upgraded per the security baseline policy

## [2.3.3] - 2026-01-14

### Added

- **CodeQL exclusion config**: `.github/codeql/codeql-config.yml` to suppress false positive alerts:
  - `py/weak-cryptographic-algorithm` — SHA1 required by HIBP API protocol
  - `py/path-injection` — `safe_path_join()` validation exists
  - `py/clear-text-logging-sensitive-data` — `redact_sensitive()` in use

### Changed

- **Documentation version sync**: Synced all documentation version references to 2.3.2.2
- **Dockerfile version label**: Updated to current version
- **Docker documentation**: Updated `DOCKER.md` and `DOCKER_PUBLISH_INSTRUCTIONS.md`

## [2.3.2.2] - 2026-01-13

### Changed

- **Test release**: Verified automatic badge updates in `/git-release` workflow

## [2.3.2.1] - 2026-01-13

### Added

- **Multi-segment version badges**: README badges with hierarchical color scheme
- **Version history table**: Shows release progression

## [2.3.2] - 2026-01-13

### Added

- **`docs/ARCHITECTURE.md`**: System architecture documentation

### Changed

- **`.gitignore` update**: Added local tool config patterns (`bandit`, `pyproject.toml`, `ruff`)

## [2.3.1] - 2026-01-09

### Added

- **CodeQL semantic analysis**: `.github/workflows/codeql.yml` workflow
- **Python security workflow**: `pip-audit`, `bandit`, `ruff` integration
- **Daily automated security scans**: Upgraded from weekly schedule

### Changed

- **Wildcard imports replaced**: Test fixtures now use explicit imports
- **`__all__` declaration**: Added to test fixtures for proper re-exports
- **Python version pinned**: Python 3.14.2 via pyenv for reproducible builds
- **Documentation versions**: Updated references from 2.0.0 to 2.3.0

### Fixed

- **GitHub workflow permissions**: Added `contents: read`
- **`.gitignore` additions**: Test artifact patterns added

### Security

- **Path traversal fix**: Fixed vulnerabilities in `dashboard/app.py` (CodeQL finding)
- **Sensitive data exposure**: Fixed logging with `redact_sensitive()` helper
- **Request timeouts**: Added 30s timeouts to prevent hanging on slow/unresponsive endpoints
- **urllib3 update**: Updated to 2.6.3 for CVE-2026-21441
- **SHA1 annotation**: Added `usedforsecurity=False` to SHA1 calls (HIBP API requirement, not cryptographic)
- **systemd hardening**: Added `ProtectSystem=strict`, `ProtectHome=read-only`

## [2.3.0] - 2025-12-29

### Added

- **Comprehensive test suite**: 203+ pytest tests achieving 85%+ coverage
- **Dockerfile HEALTHCHECK**: Container health monitoring instruction
- **Testing dependencies**: `pytest`, `pytest-cov`, `pytest-mock`, `responses`

### Changed

- **Docker Compose cleanup**: Removed obsolete `version` field from `docker-compose.yml` and `docker-compose.scheduled.yml` (deprecated in Compose v2)
- **Dockerfile metadata**: Added version label (`org.opencontainers.image.version`)

### Fixed

- **werkzeug CVE-2025-66221**: Pinned `werkzeug>=3.1.4` to address vulnerability
- **Code quality**: Removed trailing whitespace across multiple files
- **Missing docstrings**: Added to `dashboard/bitwarden_checker.py` classes

## [2.2.3] - 2025-12-27

### Changed

- **README version badges**: Updated to match VERSION file (2.2.2 → 2.2.3)

### Fixed

- **`.gitignore` addition**: Added `.exit*` pattern to exclude session timestamp files

## [2.2.2] - 2025-12-24

### Added

- **`bw-session-setup.sh`**: Helper script to set up persistent Bitwarden session
- **Bitwarden session file support**: `~/.bw_session` for dashboard integration

### Changed

- **Generic installation paths**: All hardcoded paths replaced with dynamic detection
  - Systemd services now use `HIBP_PROJECT_DIR` placeholder (auto-configured by setup script)
  - Shell scripts use `SCRIPT_DIR` for self-location
  - Documentation updated to use `<project-directory>` placeholder
- **`scripts/setup-systemd.sh`**: Auto-configures paths and installs dashboard service
- **`bitwarden_checker.py`**: Reads `BW_SESSION` from `~/.bw_session` as fallback
- **Dashboard scripts**: `start-dashboard.sh` and `launch-dashboard.sh` source `BW_SESSION` from file

### Fixed

- **Dashboard portability**: Now works for any user regardless of installation location
- **Bitwarden integration**: Works without manually exporting `BW_SESSION` each session

## [2.2.0] - 2025-12-24

### Added

- **Bitwarden Password Audit tab**: Web UI tab for password health checks
  - "Run Password Check" button to trigger `bw-hibp-stream.py`
  - Real-time progress indicator with shimmer animation
  - Results display with summary stats (Safe, Compromised, Critical, Total)
  - Compromised passwords list sorted by breach count with risk badges
  - Historical report storage (last 10 checks preserved)
  - Prerequisites check with helpful error messages
- **`bitwarden_checker.py` module**: Subprocess management and task tracking for Bitwarden integration
- **Bitwarden API endpoints**: 5 new endpoints:
  - `GET /api/bitwarden/status` — check prerequisites
  - `POST /api/bitwarden/check` — start password check
  - `GET /api/bitwarden/task/<id>` — poll task status
  - `GET /api/bitwarden/reports` — list saved reports
  - `GET /api/bitwarden/report/<filename>` — get report details

## [2.1.0] - 2025-12-24

### Added

- **`bw-hibp-stream.py`**: Streaming Bitwarden password checker
  - Reads vault items directly from `bw list items` via stdin
  - Passwords never written to disk (memory-only processing)
  - Multiple report formats: text, JSON, CSV
  - Risk level classification: Critical, High, Medium, Low
  - `--compromised-only` flag to filter results
  - Rate-limited API requests (100ms delay)

## [2.0.1] - 2025-11-24

### Added

- **New utility scripts**:
  - `check-bitwarden-passwords.py` — direct Bitwarden vault password checking
  - `check-passwords.py` — standalone password breach checker
  - `verify-dns.sh` — DNS verification utility
  - `launch-dashboard.sh` — quick dashboard launcher
- **Dashboard archive template**: `dashboard/templates/archive.html`
- **Docker and release documentation**: `DOCKER_PUBLISH_INSTRUCTIONS.md`, `GITHUB_RELEASE_INSTRUCTIONS.md`

### Changed

- **Systemd timer schedule**: Changed default from 3 AM to 2 AM
- **Boot-time fallback**: Added `OnBootSec=15min` — runs 15 minutes after boot if scheduled time was missed
- **Systemd service paths**: Updated from `~/claude-archive/projects/hibp-project` to `/hddRaid1/ClaudeCodeProjects/hibp-project`
- **`.gitignore` update**: Enhanced to exclude release artifacts

### Fixed

- **Systemd service paths**: Template paths now reference correct project directory
- **Timer resilience**: Configuration more resilient to system downtime

## [2.0.0] - 2025-11-07

### Added

- **Web dashboard**: Modern web-based dashboard for viewing breach reports and logs
  - Real-time statistics display (total scans, breaches, password exposures)
  - Interactive report browser with color-coded severity indicators
  - Built-in log viewer for workflow, systemd, and error logs
  - Auto-refresh functionality (updates every 60 seconds)
  - Download reports directly from the browser
  - Mobile-responsive design
  - Secure localhost-only access (`127.0.0.1:5000`)
- **Flask backend API**: `dashboard/app.py` with endpoints for stats, reports, logs, and downloads
- **Dashboard frontend**: Single-page HTML/CSS/JS (`dashboard/templates/index.html`)
- **Systemd service**: `dashboard/systemd/hibp-dashboard.service` for Linux auto-start
- **Cross-platform startup scripts**: Linux (`start-dashboard.sh`), Windows (`start-dashboard.ps1`), macOS (`start-dashboard-macos.sh`)
- **Dashboard documentation**: `dashboard/README.md`, `DASHBOARD_GUIDE.md`
- **Docker Compose dashboard profile**: Multi-platform Docker image support (`linux/amd64`, `linux/arm64`)
- **`requirements.txt`**: Flask >= 2.0.0, requests >= 2.25.0

### Changed

- **Docker Compose format**: Updated to v2.0 with dashboard service
- **Dockerfile**: Enhanced with Flask and dashboard dependencies
- **Project structure**: Dashboard added as first-class feature
- **README**: Dashboard-first approach in Usage section

### Security

- **Localhost-only access**: Dashboard runs on `127.0.0.1` only — no external network access
- **Read-only access**: Reports and logs are read-only
- **systemd hardening**: `PrivateTmp`, `NoNewPrivileges`

## [1.0.0] - 2025-11-07

### Added

- **Comprehensive HIBP breach checking**: Full breach detection and reporting
- **Password exposure detection**: Check passwords against known breaches
- **Stealer log mining**: Detect credentials in stealer logs
- **Critical site identification**: Flag high-risk compromised accounts
- **Pwned password checking**: k-anonymity SHA-1 range queries
- **Multi-format reporting**: JSON, CSV, and text output
- **Email list support**: Batch checking of email addresses
- **Automated scheduling**: systemd timer integration
- **Docker support**: Containerized deployment
- **Cross-platform compatibility**: Linux, Windows, macOS

[Unreleased]: https://github.com/TheBoscoClub/hibp-checker/compare/v2.3.3...HEAD
[2.3.3]: https://github.com/TheBoscoClub/hibp-checker/compare/v2.3.2.2...v2.3.3
[2.3.2.2]: https://github.com/TheBoscoClub/hibp-checker/compare/v2.3.2.1...v2.3.2.2
[2.3.2.1]: https://github.com/TheBoscoClub/hibp-checker/compare/v2.3.2...v2.3.2.1
[2.3.2]: https://github.com/TheBoscoClub/hibp-checker/compare/v2.3.1...v2.3.2
[2.3.1]: https://github.com/TheBoscoClub/hibp-checker/compare/v2.3.0...v2.3.1
[2.3.0]: https://github.com/TheBoscoClub/hibp-checker/compare/v2.2.3...v2.3.0
[2.2.3]: https://github.com/TheBoscoClub/hibp-checker/compare/v2.2.2...v2.2.3
[2.2.2]: https://github.com/TheBoscoClub/hibp-checker/compare/v2.2.0...v2.2.2
[2.2.0]: https://github.com/TheBoscoClub/hibp-checker/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/TheBoscoClub/hibp-checker/compare/v2.0.1...v2.1.0
[2.0.1]: https://github.com/TheBoscoClub/hibp-checker/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/TheBoscoClub/hibp-checker/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/TheBoscoClub/hibp-checker/releases/tag/v1.0.0
