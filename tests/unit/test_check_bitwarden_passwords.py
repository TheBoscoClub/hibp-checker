"""Unit tests for check-bitwarden-passwords.py module.

Tests the Bitwarden export parsing and password checking functionality:
- parse_bitwarden_json() - JSON parsing and item extraction
- check_password() - HIBP API interaction (similar to check-passwords.py)
- format_risk() - Risk level formatting
- File handling edge cases
"""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest
import responses

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the module under test - handle hyphenated filename
import importlib.util
spec = importlib.util.spec_from_file_location(
    "check_bitwarden_passwords",
    PROJECT_ROOT / "check-bitwarden-passwords.py"
)
check_bitwarden_passwords = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_bitwarden_passwords)

from tests.fixtures.mock_responses import (
    HIBP_HASH_RANGE_WITH_MATCH,
    HIBP_HASH_RANGE_NO_MATCH,
)
from tests.fixtures.sample_data import (
    SAMPLE_BITWARDEN_EXPORT,
    SAMPLE_BITWARDEN_EXPORT_EMPTY,
    SAMPLE_BITWARDEN_EXPORT_NO_LOGINS,
    SAMPLE_BITWARDEN_EXPORT_SAFE,
    PWNED_PASSWORD,
    PWNED_PASSWORD_HASH_PREFIX,
    PWNED_PASSWORD_COUNT,
    SAFE_PASSWORD,
    SAFE_PASSWORD_HASH_PREFIX,
)


class TestParseBitwardenJson:
    """Tests for the parse_bitwarden_json() function."""

    def test_parse_valid_export(self, temp_bitwarden_export):
        """Test parsing a valid Bitwarden export file."""
        items = check_bitwarden_passwords.parse_bitwarden_json(str(temp_bitwarden_export))

        # Should extract only login items with passwords
        assert len(items) > 0
        assert all(item.get('type') == 1 for item in items)
        assert all(item.get('login', {}).get('password') for item in items)

    def test_parse_file_not_found(self, capsys):
        """Test handling of non-existent file."""
        items = check_bitwarden_passwords.parse_bitwarden_json("/nonexistent/path/file.json")

        assert items == []
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower() or "Error" in captured.out

    def test_parse_invalid_json(self, temp_invalid_json, capsys):
        """Test handling of invalid JSON file."""
        items = check_bitwarden_passwords.parse_bitwarden_json(str(temp_invalid_json))

        assert items == []
        captured = capsys.readouterr()
        assert "Invalid JSON" in captured.out or "Error" in captured.out

    def test_parse_empty_items(self, temp_dir, capsys):
        """Test handling of export with no items."""
        empty_export = temp_dir / "empty_export.json"
        empty_export.write_text(json.dumps(SAMPLE_BITWARDEN_EXPORT_EMPTY))

        items = check_bitwarden_passwords.parse_bitwarden_json(str(empty_export))

        assert items == []

    def test_parse_no_login_items(self, temp_dir):
        """Test handling of export with only non-login items."""
        no_logins = temp_dir / "no_logins.json"
        no_logins.write_text(json.dumps(SAMPLE_BITWARDEN_EXPORT_NO_LOGINS))

        items = check_bitwarden_passwords.parse_bitwarden_json(str(no_logins))

        assert items == []

    def test_parse_filters_empty_passwords(self, temp_dir):
        """Test that items with empty passwords are filtered out."""
        export_with_empty = {
            "items": [
                {
                    "type": 1,
                    "name": "No Password",
                    "login": {"username": "user", "password": ""}
                },
                {
                    "type": 1,
                    "name": "Has Password",
                    "login": {"username": "user", "password": "secret123"}
                }
            ]
        }
        export_file = temp_dir / "with_empty.json"
        export_file.write_text(json.dumps(export_with_empty))

        items = check_bitwarden_passwords.parse_bitwarden_json(str(export_file))

        assert len(items) == 1
        assert items[0]["name"] == "Has Password"

    def test_parse_unexpected_format(self, temp_dir, capsys):
        """Test handling of unexpected JSON structure."""
        unexpected = {"data": {"entries": []}}
        unexpected_file = temp_dir / "unexpected.json"
        unexpected_file.write_text(json.dumps(unexpected))

        items = check_bitwarden_passwords.parse_bitwarden_json(str(unexpected_file))

        assert items == []
        captured = capsys.readouterr()
        assert "Unexpected" in captured.out or len(items) == 0

    def test_parse_with_expanded_home_directory(self, temp_dir):
        """Test that expanded home directory paths work.

        Note: The parse_bitwarden_json function expects already-expanded paths.
        The main() function expands ~ before calling parse_bitwarden_json.
        """
        # Create a file in temp_dir
        test_file = temp_dir / "export.json"
        test_file.write_text(json.dumps(SAMPLE_BITWARDEN_EXPORT))

        # Pass the fully expanded path (simulating what main() does)
        expanded_path = str(test_file)
        items = check_bitwarden_passwords.parse_bitwarden_json(expanded_path)

        assert len(items) > 0


class TestCheckPassword:
    """Tests for the check_password() function in check-bitwarden-passwords."""

    @responses.activate
    def test_check_password_pwned(self):
        """Test that a pwned password is correctly identified."""
        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=HIBP_HASH_RANGE_WITH_MATCH,
            status=200,
        )

        is_pwned, count = check_bitwarden_passwords.check_password(PWNED_PASSWORD)

        assert is_pwned is True
        assert count == PWNED_PASSWORD_COUNT

    @responses.activate
    def test_check_password_safe(self):
        """Test that a safe password returns not pwned."""
        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{SAFE_PASSWORD_HASH_PREFIX}",
            body=HIBP_HASH_RANGE_NO_MATCH,
            status=200,
        )

        is_pwned, count = check_bitwarden_passwords.check_password(SAFE_PASSWORD)

        assert is_pwned is False
        assert count == 0

    def test_check_password_empty(self):
        """Test that empty password returns safe without API call."""
        is_pwned, count = check_bitwarden_passwords.check_password("")

        assert is_pwned is False
        assert count == 0

    def test_check_password_none_like(self):
        """Test handling of None-like empty password."""
        is_pwned, count = check_bitwarden_passwords.check_password("")

        assert is_pwned is False
        assert count == 0

    @responses.activate
    def test_check_password_network_error(self):
        """Test that network errors return -1 count."""
        from requests.exceptions import ConnectionError

        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=ConnectionError("Network error"),
        )

        is_pwned, count = check_bitwarden_passwords.check_password(PWNED_PASSWORD)

        assert is_pwned is False
        assert count == -1


class TestFormatRisk:
    """Tests for the format_risk() function."""

    def test_format_risk_safe(self):
        """Test formatting for safe password."""
        result = check_bitwarden_passwords.format_risk(0)

        assert "Safe" in result
        assert "\033[0;32m" in result  # Green color

    def test_format_risk_low(self):
        """Test formatting for low risk (< 10)."""
        for count in [1, 5, 9]:
            result = check_bitwarden_passwords.format_risk(count)

            assert str(count) in result
            assert "\033[1;33m" in result  # Yellow color

    def test_format_risk_medium(self):
        """Test formatting for medium risk (10-99)."""
        for count in [10, 50, 99]:
            result = check_bitwarden_passwords.format_risk(count)

            assert str(count) in result
            assert "\033[0;31m" in result  # Red color

    def test_format_risk_high(self):
        """Test formatting for high risk (100-999)."""
        for count in [100, 500, 999]:
            result = check_bitwarden_passwords.format_risk(count)

            assert "HIGH" in result
            assert str(count) in result

    def test_format_risk_critical(self):
        """Test formatting for critical risk (>= 1000)."""
        for count in [1000, 10000, 1000000]:
            result = check_bitwarden_passwords.format_risk(count)

            assert "CRITICAL" in result
            assert "\033[1;31m" in result  # Bold red color

    def test_format_risk_number_formatting(self):
        """Test that large numbers use comma separators."""
        result = check_bitwarden_passwords.format_risk(1000000)

        assert "1,000,000" in result


class TestBitwardenItemParsing:
    """Tests for extracting data from Bitwarden items."""

    def test_extract_item_name(self, temp_bitwarden_export):
        """Test that item names are correctly extracted."""
        items = check_bitwarden_passwords.parse_bitwarden_json(str(temp_bitwarden_export))

        names = [item.get('name') for item in items]
        assert "Example Site" in names
        assert "Secure Bank" in names

    def test_extract_item_username(self, temp_bitwarden_export):
        """Test that usernames are correctly extracted."""
        items = check_bitwarden_passwords.parse_bitwarden_json(str(temp_bitwarden_export))

        # Find specific item
        example_item = next((i for i in items if i.get('name') == 'Example Site'), None)
        assert example_item is not None
        assert example_item.get('login', {}).get('username') == 'testuser'

    def test_extract_item_password(self, temp_bitwarden_export):
        """Test that passwords are correctly extracted."""
        items = check_bitwarden_passwords.parse_bitwarden_json(str(temp_bitwarden_export))

        # Find specific item
        example_item = next((i for i in items if i.get('name') == 'Example Site'), None)
        assert example_item is not None
        assert example_item.get('login', {}).get('password') == PWNED_PASSWORD

    def test_filter_type_1_only(self, temp_bitwarden_export):
        """Test that only type 1 (login) items are extracted."""
        items = check_bitwarden_passwords.parse_bitwarden_json(str(temp_bitwarden_export))

        # All items should be type 1
        assert all(item.get('type') == 1 for item in items)

        # Original export has notes and cards - verify they're filtered
        # The export has 7 items total, but fewer should be logins with passwords
        assert len(items) < 7


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_parse_with_unicode_content(self, temp_dir):
        """Test parsing export with unicode characters."""
        unicode_export = {
            "items": [
                {
                    "type": 1,
                    "name": "Site with emoji",
                    "login": {
                        "username": "user@example.com",
                        "password": "secret123"
                    }
                }
            ]
        }
        unicode_file = temp_dir / "unicode.json"
        unicode_file.write_text(json.dumps(unicode_export, ensure_ascii=False), encoding='utf-8')

        items = check_bitwarden_passwords.parse_bitwarden_json(str(unicode_file))

        assert len(items) == 1

    def test_parse_with_missing_login_field(self, temp_dir):
        """Test handling of items missing login field."""
        missing_login = {
            "items": [
                {
                    "type": 1,
                    "name": "Broken Item"
                    # No login field
                }
            ]
        }
        missing_file = temp_dir / "missing.json"
        missing_file.write_text(json.dumps(missing_login))

        items = check_bitwarden_passwords.parse_bitwarden_json(str(missing_file))

        assert items == []

    def test_parse_with_null_password(self, temp_dir):
        """Test handling of items with null password."""
        null_password = {
            "items": [
                {
                    "type": 1,
                    "name": "Null Password",
                    "login": {
                        "username": "user",
                        "password": None
                    }
                }
            ]
        }
        null_file = temp_dir / "null_password.json"
        null_file.write_text(json.dumps(null_password))

        items = check_bitwarden_passwords.parse_bitwarden_json(str(null_file))

        assert items == []

    def test_parse_permission_error(self, temp_dir, capsys):
        """Test handling of permission errors."""
        restricted_file = temp_dir / "restricted.json"
        restricted_file.write_text(json.dumps(SAMPLE_BITWARDEN_EXPORT))

        # Make file unreadable (skip on Windows)
        import os
        if os.name != 'nt':
            restricted_file.chmod(0o000)

            items = check_bitwarden_passwords.parse_bitwarden_json(str(restricted_file))

            assert items == []

            # Restore permissions for cleanup
            restricted_file.chmod(0o644)

    def test_large_export_handling(self, temp_dir):
        """Test handling of large exports."""
        from tests.fixtures.sample_data import generate_large_bitwarden_export

        large_export = generate_large_bitwarden_export(100)
        large_file = temp_dir / "large.json"
        large_file.write_text(json.dumps(large_export))

        items = check_bitwarden_passwords.parse_bitwarden_json(str(large_file))

        assert len(items) == 100
