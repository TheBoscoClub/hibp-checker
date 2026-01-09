"""Shared pytest fixtures and configuration for HIBP Project tests.

This module provides common fixtures used across all test modules including:
- Mock HIBP API responses
- Temporary file/directory fixtures
- Sample Bitwarden export data
- Request mocking utilities
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest
import responses

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / 'dashboard'))

from tests.fixtures.mock_responses import (
    HIBP_HASH_RANGE_WITH_MATCH,
    HIBP_HASH_RANGE_NO_MATCH,
    HIBP_BREACH_RESPONSE,
    HIBP_PASTE_RESPONSE,
    HIBP_STEALER_LOGS_RESPONSE,
)
from tests.fixtures.sample_data import (
    SAMPLE_BITWARDEN_EXPORT,
    SAMPLE_BITWARDEN_ITEMS,
    SAFE_PASSWORD,
    PWNED_PASSWORD,
    PWNED_PASSWORD_HASH_PREFIX,
)


# =============================================================================
# HIBP API Mock Fixtures
# =============================================================================

@pytest.fixture
def mock_hibp_api():
    """Activate responses mock for HIBP API calls.

    This fixture mocks all HIBP API endpoints and allows tests to add
    custom responses for specific test scenarios.

    Yields:
        responses.RequestsMock: The active mock object for adding responses.
    """
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def mock_hibp_password_found(mock_hibp_api):
    """Mock HIBP API to return a found password (pwned).

    Uses the pwned password hash prefix to return a matching response.
    """
    mock_hibp_api.add(
        responses.GET,
        f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
        body=HIBP_HASH_RANGE_WITH_MATCH,
        status=200,
    )
    return mock_hibp_api


@pytest.fixture
def mock_hibp_password_safe(mock_hibp_api):
    """Mock HIBP API to return no match (safe password)."""
    # Use a different prefix that won't match our test passwords
    mock_hibp_api.add(
        responses.GET,
        responses.matchers.UrlMatcher.from_string("https://api.pwnedpasswords.com/range/"),
        body=HIBP_HASH_RANGE_NO_MATCH,
        status=200,
    )
    return mock_hibp_api


@pytest.fixture
def mock_hibp_api_error(mock_hibp_api):
    """Mock HIBP API to return an error response."""
    mock_hibp_api.add(
        responses.GET,
        responses.matchers.UrlMatcher.from_string("https://api.pwnedpasswords.com/range/"),
        body="Service unavailable",
        status=503,
    )
    return mock_hibp_api


@pytest.fixture
def mock_hibp_api_timeout(mock_hibp_api):
    """Mock HIBP API to simulate a timeout."""
    from requests.exceptions import Timeout

    mock_hibp_api.add(
        responses.GET,
        responses.matchers.UrlMatcher.from_string("https://api.pwnedpasswords.com/range/"),
        body=Timeout("Connection timed out"),
    )
    return mock_hibp_api


@pytest.fixture
def mock_hibp_breach_api(mock_hibp_api):
    """Mock HIBP breach API endpoints."""
    mock_hibp_api.add(
        responses.GET,
        responses.matchers.UrlMatcher.from_string("https://haveibeenpwned.com/api/v3/breachedaccount/"),
        json=HIBP_BREACH_RESPONSE,
        status=200,
    )
    mock_hibp_api.add(
        responses.GET,
        responses.matchers.UrlMatcher.from_string("https://haveibeenpwned.com/api/v3/pasteaccount/"),
        json=HIBP_PASTE_RESPONSE,
        status=200,
    )
    mock_hibp_api.add(
        responses.GET,
        responses.matchers.UrlMatcher.from_string("https://haveibeenpwned.com/api/v3/stealerlogsbyemail/"),
        json=HIBP_STEALER_LOGS_RESPONSE,
        status=200,
    )
    return mock_hibp_api


# =============================================================================
# File System Fixtures
# =============================================================================

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test file operations.

    Yields:
        Path: Path to the temporary directory.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_bitwarden_export(temp_dir) -> Path:
    """Create a temporary Bitwarden JSON export file.

    Args:
        temp_dir: The temporary directory fixture.

    Returns:
        Path: Path to the created export file.
    """
    export_file = temp_dir / "bitwarden_export.json"
    export_file.write_text(json.dumps(SAMPLE_BITWARDEN_EXPORT))
    return export_file


@pytest.fixture
def temp_empty_file(temp_dir) -> Path:
    """Create a temporary empty file.

    Returns:
        Path: Path to the empty file.
    """
    empty_file = temp_dir / "empty.json"
    empty_file.write_text("")
    return empty_file


@pytest.fixture
def temp_invalid_json(temp_dir) -> Path:
    """Create a temporary file with invalid JSON.

    Returns:
        Path: Path to the invalid JSON file.
    """
    invalid_file = temp_dir / "invalid.json"
    invalid_file.write_text("{not valid json")
    return invalid_file


@pytest.fixture
def temp_report_file(temp_dir) -> Path:
    """Create a temporary HIBP report file.

    Returns:
        Path: Path to the report file.
    """
    report_content = """HIBP COMPREHENSIVE BREACH REPORT
Generated: 2024-01-15T10:30:00
============================================================

SUMMARY
------------------------------
Total Breaches: 5
Password Exposures: 2
Stealer Log Hits: 1
Critical Sites Compromised: 1
Paste Exposures: 3

EMAIL: test@example.com
------------------------------
Total Breaches: 5

Password Exposed In:
  - Adobe (2013-10-04) - Type: plaintext
  - LinkedIn (2016-05-18) - Type: sha1_hash

============================================================
"""
    report_file = temp_dir / "hibp_report_20240115_103000.txt"
    report_file.write_text(report_content)
    return report_file


# =============================================================================
# Bitwarden Fixtures
# =============================================================================

@pytest.fixture
def sample_bitwarden_items():
    """Return sample Bitwarden vault items for testing.

    Returns:
        list: List of Bitwarden login items.
    """
    return SAMPLE_BITWARDEN_ITEMS.copy()


@pytest.fixture
def mock_bw_session(monkeypatch):
    """Mock BW_SESSION environment variable.

    Sets a fake Bitwarden session token for testing.
    """
    monkeypatch.setenv("BW_SESSION", "fake_session_token_for_testing")


@pytest.fixture
def mock_bw_cli(mocker):
    """Mock the Bitwarden CLI subprocess calls.

    Returns:
        MagicMock: The mocked subprocess.run function.
    """
    mock_run = mocker.patch("subprocess.run")

    # Default: bw is installed and vault is unlocked
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout=json.dumps({"status": "unlocked"}),
        stderr="",
    )

    return mock_run


# =============================================================================
# Flask App Fixtures
# =============================================================================

@pytest.fixture
def flask_app():
    """Create a Flask test app instance.

    Returns:
        Flask: The Flask application configured for testing.
    """
    # Import here to avoid circular imports
    from dashboard.app import app

    app.config.update({
        "TESTING": True,
        "DEBUG": False,
    })
    return app


@pytest.fixture
def flask_client(flask_app):
    """Create a Flask test client.

    Returns:
        FlaskClient: The test client for making requests.
    """
    return flask_app.test_client()


@pytest.fixture
def flask_runner(flask_app):
    """Create a Flask CLI test runner.

    Returns:
        FlaskCliRunner: The CLI test runner.
    """
    return flask_app.test_cli_runner()


# =============================================================================
# Requests Mocking Fixtures
# =============================================================================

@pytest.fixture
def mock_requests_get(mocker):
    """Mock requests.get for unit tests.

    Returns:
        MagicMock: The mocked requests.get function.
    """
    return mocker.patch("requests.get")


@pytest.fixture
def mock_requests_timeout(mock_requests_get):
    """Configure requests.get to raise a timeout exception."""
    from requests.exceptions import Timeout

    mock_requests_get.side_effect = Timeout("Connection timed out")
    return mock_requests_get


@pytest.fixture
def mock_requests_connection_error(mock_requests_get):
    """Configure requests.get to raise a connection error."""
    from requests.exceptions import ConnectionError

    mock_requests_get.side_effect = ConnectionError("Failed to connect")
    return mock_requests_get


# =============================================================================
# Password Test Data Fixtures
# =============================================================================

@pytest.fixture
def safe_password():
    """Return a password that is not in the HIBP database."""
    return SAFE_PASSWORD


@pytest.fixture
def pwned_password():
    """Return a password that IS in the HIBP database."""
    return PWNED_PASSWORD


# =============================================================================
# Cleanup and Environment Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    """Clean up environment variables that might affect tests.

    This fixture runs automatically for all tests.
    """
    # Remove any existing HIBP-related env vars
    for key in list(os.environ.keys()):
        if key.startswith("HIBP_") or key == "BW_SESSION":
            monkeypatch.delenv(key, raising=False)


@pytest.fixture
def capture_stderr(capsys):
    """Fixture to capture stderr output.

    Returns:
        Callable: Function to get captured stderr.
    """
    def get_stderr():
        captured = capsys.readouterr()
        return captured.err

    return get_stderr
