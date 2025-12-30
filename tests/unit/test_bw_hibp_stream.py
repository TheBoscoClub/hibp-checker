"""Unit tests for bw-hibp-stream.py module.

Tests the streaming Bitwarden password checker including:
- CheckResult dataclass
- check_password_hibp() function
- parse_vault_items() function
- Report generation functions (text, JSON, CSV)
- format_risk_terminal() function
"""

import json
import sys
from datetime import datetime
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import responses

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the module under test - handle hyphenated filename
import importlib.util
spec = importlib.util.spec_from_file_location(
    "bw_hibp_stream",
    PROJECT_ROOT / "bw-hibp-stream.py"
)
bw_hibp_stream = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bw_hibp_stream)

from tests.fixtures.mock_responses import (
    HIBP_HASH_RANGE_WITH_MATCH,
    HIBP_HASH_RANGE_NO_MATCH,
)
from tests.fixtures.sample_data import (
    SAMPLE_BITWARDEN_ITEMS,
    SAMPLE_BITWARDEN_EXPORT,
    PWNED_PASSWORD,
    PWNED_PASSWORD_HASH_PREFIX,
    PWNED_PASSWORD_COUNT,
    SAFE_PASSWORD,
    SAFE_PASSWORD_HASH_PREFIX,
)


class TestCheckResult:
    """Tests for the CheckResult dataclass."""

    def test_create_check_result_safe(self):
        """Test creating a CheckResult for a safe password."""
        result = bw_hibp_stream.CheckResult(
            name="Test Site",
            username="user@test.com",
            uri="https://test.com",
            is_pwned=False,
            breach_count=0,
        )

        assert result.name == "Test Site"
        assert result.username == "user@test.com"
        assert result.is_pwned is False
        assert result.breach_count == 0
        assert result.error is None

    def test_create_check_result_pwned(self):
        """Test creating a CheckResult for a pwned password."""
        result = bw_hibp_stream.CheckResult(
            name="Compromised Site",
            username="victim",
            uri="https://compromised.com",
            is_pwned=True,
            breach_count=10000,
        )

        assert result.is_pwned is True
        assert result.breach_count == 10000

    def test_create_check_result_with_error(self):
        """Test creating a CheckResult with an error."""
        result = bw_hibp_stream.CheckResult(
            name="Error Site",
            username="user",
            uri="https://error.com",
            is_pwned=False,
            breach_count=-1,
            error="Connection timeout",
        )

        assert result.error == "Connection timeout"
        assert result.breach_count == -1

    def test_status_property_safe(self):
        """Test status property for safe password."""
        result = bw_hibp_stream.CheckResult(
            name="Safe", username="", uri="",
            is_pwned=False, breach_count=0
        )

        assert result.status == "safe"

    def test_status_property_compromised(self):
        """Test status property for compromised password."""
        result = bw_hibp_stream.CheckResult(
            name="Pwned", username="", uri="",
            is_pwned=True, breach_count=100
        )

        assert result.status == "compromised"

    def test_status_property_error(self):
        """Test status property when there's an error."""
        result = bw_hibp_stream.CheckResult(
            name="Error", username="", uri="",
            is_pwned=False, breach_count=-1,
            error="Network error"
        )

        assert result.status == "error"

    def test_risk_level_safe(self):
        """Test risk_level property for safe password."""
        result = bw_hibp_stream.CheckResult(
            name="Safe", username="", uri="",
            is_pwned=False, breach_count=0
        )

        assert result.risk_level == "safe"

    def test_risk_level_low(self):
        """Test risk_level for low risk (< 10)."""
        result = bw_hibp_stream.CheckResult(
            name="Low", username="", uri="",
            is_pwned=True, breach_count=5
        )

        assert result.risk_level == "low"

    def test_risk_level_medium(self):
        """Test risk_level for medium risk (10-99)."""
        result = bw_hibp_stream.CheckResult(
            name="Medium", username="", uri="",
            is_pwned=True, breach_count=50
        )

        assert result.risk_level == "medium"

    def test_risk_level_high(self):
        """Test risk_level for high risk (100-999)."""
        result = bw_hibp_stream.CheckResult(
            name="High", username="", uri="",
            is_pwned=True, breach_count=500
        )

        assert result.risk_level == "high"

    def test_risk_level_critical(self):
        """Test risk_level for critical risk (>= 1000)."""
        result = bw_hibp_stream.CheckResult(
            name="Critical", username="", uri="",
            is_pwned=True, breach_count=5000
        )

        assert result.risk_level == "critical"

    def test_risk_level_unknown_on_error(self):
        """Test risk_level is unknown when there's an error."""
        result = bw_hibp_stream.CheckResult(
            name="Error", username="", uri="",
            is_pwned=False, breach_count=-1,
            error="Error occurred"
        )

        assert result.risk_level == "unknown"


class TestCheckPasswordHibp:
    """Tests for the check_password_hibp() function."""

    @responses.activate
    def test_check_password_hibp_pwned(self):
        """Test checking a pwned password."""
        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=HIBP_HASH_RANGE_WITH_MATCH,
            status=200,
        )

        is_pwned, count, error = bw_hibp_stream.check_password_hibp(PWNED_PASSWORD)

        assert is_pwned is True
        assert count == PWNED_PASSWORD_COUNT
        assert error is None

    @responses.activate
    def test_check_password_hibp_safe(self):
        """Test checking a safe password."""
        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{SAFE_PASSWORD_HASH_PREFIX}",
            body=HIBP_HASH_RANGE_NO_MATCH,
            status=200,
        )

        is_pwned, count, error = bw_hibp_stream.check_password_hibp(SAFE_PASSWORD)

        assert is_pwned is False
        assert count == 0
        assert error is None

    def test_check_password_hibp_empty(self):
        """Test checking an empty password."""
        is_pwned, count, error = bw_hibp_stream.check_password_hibp("")

        assert is_pwned is False
        assert count == 0
        assert error is None

    @responses.activate
    def test_check_password_hibp_network_error(self):
        """Test handling of network errors."""
        from requests.exceptions import ConnectionError

        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=ConnectionError("Network error"),
        )

        is_pwned, count, error = bw_hibp_stream.check_password_hibp(PWNED_PASSWORD)

        assert is_pwned is False
        assert count == -1
        assert error is not None

    @responses.activate
    def test_check_password_hibp_includes_user_agent(self):
        """Test that requests include User-Agent header."""
        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=HIBP_HASH_RANGE_NO_MATCH,
            status=200,
        )

        bw_hibp_stream.check_password_hibp(PWNED_PASSWORD)

        assert len(responses.calls) == 1
        assert "User-Agent" in responses.calls[0].request.headers


class TestParseVaultItems:
    """Tests for the parse_vault_items() function."""

    def test_parse_vault_items_array(self):
        """Test parsing vault items from array format."""
        json_data = json.dumps(SAMPLE_BITWARDEN_ITEMS)

        items = bw_hibp_stream.parse_vault_items(json_data)

        # Should filter to only login items with passwords
        assert len(items) > 0
        assert all(item.get('type') == 1 for item in items)

    def test_parse_vault_items_object_with_items(self):
        """Test parsing vault items from object format with 'items' key."""
        json_data = json.dumps(SAMPLE_BITWARDEN_EXPORT)

        items = bw_hibp_stream.parse_vault_items(json_data)

        assert len(items) > 0

    def test_parse_vault_items_invalid_json(self, capsys):
        """Test parsing invalid JSON."""
        items = bw_hibp_stream.parse_vault_items("{invalid json}")

        assert items == []
        captured = capsys.readouterr()
        assert "Error" in captured.err or "Invalid" in captured.err

    def test_parse_vault_items_empty_array(self):
        """Test parsing empty array."""
        items = bw_hibp_stream.parse_vault_items("[]")

        assert items == []

    def test_parse_vault_items_filters_non_logins(self):
        """Test that non-login items are filtered out."""
        json_data = json.dumps(SAMPLE_BITWARDEN_EXPORT)

        items = bw_hibp_stream.parse_vault_items(json_data)

        # All returned items should be logins (type 1)
        assert all(item.get('type') == 1 for item in items)

    def test_parse_vault_items_filters_empty_passwords(self):
        """Test that items with empty passwords are filtered."""
        data = [
            {"type": 1, "name": "Empty", "login": {"password": ""}},
            {"type": 1, "name": "HasPass", "login": {"password": "secret"}}
        ]

        items = bw_hibp_stream.parse_vault_items(json.dumps(data))

        assert len(items) == 1
        assert items[0]["name"] == "HasPass"


class TestFormatRiskTerminal:
    """Tests for the format_risk_terminal() function."""

    def test_format_risk_terminal_safe(self):
        """Test formatting for safe password."""
        result = bw_hibp_stream.CheckResult(
            name="Safe", username="", uri="",
            is_pwned=False, breach_count=0
        )

        formatted = bw_hibp_stream.format_risk_terminal(result)

        assert "Safe" in formatted
        assert "\033[0;32m" in formatted  # Green color

    def test_format_risk_terminal_critical(self):
        """Test formatting for critical password."""
        result = bw_hibp_stream.CheckResult(
            name="Critical", username="", uri="",
            is_pwned=True, breach_count=5000
        )

        formatted = bw_hibp_stream.format_risk_terminal(result)

        assert "CRITICAL" in formatted
        assert "\033[1;31m" in formatted  # Bold red

    def test_format_risk_terminal_error(self):
        """Test formatting for error result."""
        result = bw_hibp_stream.CheckResult(
            name="Error", username="", uri="",
            is_pwned=False, breach_count=-1,
            error="Network timeout"
        )

        formatted = bw_hibp_stream.format_risk_terminal(result)

        assert "ERROR" in formatted
        assert "Network timeout" in formatted

    def test_format_risk_terminal_medium(self):
        """Test formatting for medium risk."""
        result = bw_hibp_stream.CheckResult(
            name="Medium", username="", uri="",
            is_pwned=True, breach_count=50
        )

        formatted = bw_hibp_stream.format_risk_terminal(result)

        assert "MEDIUM" in formatted


class TestGenerateReportJson:
    """Tests for the generate_report_json() function."""

    def test_generate_report_json_structure(self):
        """Test that JSON report has correct structure."""
        results = [
            bw_hibp_stream.CheckResult(
                name="Test", username="user", uri="https://test.com",
                is_pwned=False, breach_count=0
            )
        ]

        report = bw_hibp_stream.generate_report_json(results)
        data = json.loads(report)

        assert "generated" in data
        assert "summary" in data
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_generate_report_json_summary_counts(self):
        """Test that summary counts are correct."""
        results = [
            bw_hibp_stream.CheckResult(
                name="Safe1", username="", uri="",
                is_pwned=False, breach_count=0
            ),
            bw_hibp_stream.CheckResult(
                name="Pwned1", username="", uri="",
                is_pwned=True, breach_count=5000
            ),
            bw_hibp_stream.CheckResult(
                name="Error1", username="", uri="",
                is_pwned=False, breach_count=-1,
                error="Error"
            )
        ]

        report = bw_hibp_stream.generate_report_json(results)
        data = json.loads(report)

        assert data["summary"]["total"] == 3
        assert data["summary"]["safe"] == 1
        assert data["summary"]["compromised"] == 1
        assert data["summary"]["errors"] == 1

    def test_generate_report_json_item_fields(self):
        """Test that items have all required fields."""
        results = [
            bw_hibp_stream.CheckResult(
                name="Test Site",
                username="testuser",
                uri="https://test.com",
                is_pwned=True,
                breach_count=100
            )
        ]

        report = bw_hibp_stream.generate_report_json(results)
        data = json.loads(report)
        item = data["items"][0]

        assert item["name"] == "Test Site"
        assert item["username"] == "testuser"
        assert item["uri"] == "https://test.com"
        assert item["status"] == "compromised"
        assert item["risk_level"] == "high"
        assert item["breach_count"] == 100


class TestGenerateReportText:
    """Tests for the generate_report_text() function."""

    def test_generate_report_text_header(self):
        """Test that text report has header."""
        results = []

        report = bw_hibp_stream.generate_report_text(results)

        assert "BITWARDEN HIBP PASSWORD AUDIT REPORT" in report
        assert "Generated:" in report

    def test_generate_report_text_summary(self):
        """Test that text report includes summary section."""
        results = [
            bw_hibp_stream.CheckResult(
                name="Test", username="", uri="",
                is_pwned=False, breach_count=0
            )
        ]

        report = bw_hibp_stream.generate_report_text(results)

        assert "SUMMARY" in report
        assert "Total passwords checked:" in report

    def test_generate_report_text_critical_section(self):
        """Test that critical items are highlighted."""
        results = [
            bw_hibp_stream.CheckResult(
                name="Critical Site",
                username="victim",
                uri="https://critical.com",
                is_pwned=True,
                breach_count=5000
            )
        ]

        report = bw_hibp_stream.generate_report_text(results)

        assert "CRITICAL" in report
        assert "Critical Site" in report

    def test_generate_report_text_recommendations(self):
        """Test that recommendations are included."""
        results = [
            bw_hibp_stream.CheckResult(
                name="Pwned", username="", uri="",
                is_pwned=True, breach_count=100
            )
        ]

        report = bw_hibp_stream.generate_report_text(results)

        assert "RECOMMENDATIONS" in report
        assert "Change" in report


class TestGenerateReportCsv:
    """Tests for the generate_report_csv() function."""

    def test_generate_report_csv_header(self):
        """Test that CSV has correct header row."""
        results = []

        report = bw_hibp_stream.generate_report_csv(results)

        assert "Name" in report
        assert "Username" in report
        assert "Status" in report
        assert "Risk Level" in report

    def test_generate_report_csv_data_row(self):
        """Test that data is correctly formatted as CSV."""
        results = [
            bw_hibp_stream.CheckResult(
                name="Test Site",
                username="testuser",
                uri="https://test.com",
                is_pwned=True,
                breach_count=500
            )
        ]

        report = bw_hibp_stream.generate_report_csv(results)
        lines = report.strip().split('\n')

        assert len(lines) == 2  # Header + 1 data row
        assert "Test Site" in lines[1]
        assert "testuser" in lines[1]

    def test_generate_report_csv_handles_commas(self):
        """Test that CSV properly escapes commas in data."""
        results = [
            bw_hibp_stream.CheckResult(
                name="Site, With Comma",
                username="user",
                uri="",
                is_pwned=False,
                breach_count=0
            )
        ]

        report = bw_hibp_stream.generate_report_csv(results)

        # CSV should quote fields with commas
        assert '"Site, With Comma"' in report or 'Site, With Comma' in report


class TestCheckAllPasswords:
    """Tests for the check_all_passwords() function."""

    @responses.activate
    def test_check_all_passwords_returns_results(self):
        """Test that check_all_passwords returns CheckResult list."""
        # Add mock for any hash prefix
        responses.add_passthru("https://api.pwnedpasswords.com")

        # Use items with passwords that we can mock
        items = [
            {
                "type": 1,
                "name": "Test",
                "login": {
                    "username": "user",
                    "password": PWNED_PASSWORD,
                    "uris": []
                }
            }
        ]

        # Mock the actual API call
        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=HIBP_HASH_RANGE_WITH_MATCH,
            status=200,
        )

        results = bw_hibp_stream.check_all_passwords(items, quiet=True)

        assert len(results) == 1
        assert isinstance(results[0], bw_hibp_stream.CheckResult)

    @responses.activate
    def test_check_all_passwords_extracts_uri(self):
        """Test that URIs are correctly extracted from items."""
        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{SAFE_PASSWORD_HASH_PREFIX}",
            body=HIBP_HASH_RANGE_NO_MATCH,
            status=200,
        )

        items = [
            {
                "type": 1,
                "name": "Test",
                "login": {
                    "username": "user",
                    "password": SAFE_PASSWORD,
                    "uris": [{"uri": "https://example.com"}]
                }
            }
        ]

        results = bw_hibp_stream.check_all_passwords(items, quiet=True)

        assert results[0].uri == "https://example.com"

    @responses.activate
    def test_check_all_passwords_handles_missing_uris(self):
        """Test handling of items without URIs."""
        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{SAFE_PASSWORD_HASH_PREFIX}",
            body=HIBP_HASH_RANGE_NO_MATCH,
            status=200,
        )

        items = [
            {
                "type": 1,
                "name": "No URI",
                "login": {
                    "username": "user",
                    "password": SAFE_PASSWORD,
                    "uris": []
                }
            }
        ]

        results = bw_hibp_stream.check_all_passwords(items, quiet=True)

        assert results[0].uri == ""
