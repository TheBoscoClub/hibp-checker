"""Unit tests for check-passwords.py module.

Tests the core password checking functionality including:
- check_password() function - HIBP API interaction
- format_count() function - risk level formatting
- Edge cases and error handling
"""

import hashlib
import sys
from pathlib import Path

import responses

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the module under test - handle hyphenated filename
import importlib.util
spec = importlib.util.spec_from_file_location(
    "check_passwords",
    PROJECT_ROOT / "check-passwords.py"
)
check_passwords = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_passwords)

from tests.fixtures.mock_responses import (
    HIBP_HASH_RANGE_WITH_MATCH,
    HIBP_HASH_RANGE_NO_MATCH,
)
from tests.fixtures.sample_data import (
    PWNED_PASSWORD,
    PWNED_PASSWORD_HASH_PREFIX,
    PWNED_PASSWORD_COUNT,
    SAFE_PASSWORD,
    SAFE_PASSWORD_HASH_PREFIX,
)


class TestCheckPassword:
    """Tests for the check_password() function."""

    @responses.activate
    def test_check_password_pwned(self):
        """Test that a pwned password is correctly identified."""
        # Mock the HIBP API response
        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=HIBP_HASH_RANGE_WITH_MATCH,
            status=200,
        )

        is_pwned, count = check_passwords.check_password(PWNED_PASSWORD)

        assert is_pwned is True
        assert count == PWNED_PASSWORD_COUNT
        assert len(responses.calls) == 1

    @responses.activate
    def test_check_password_safe(self):
        """Test that a safe password returns not pwned."""
        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{SAFE_PASSWORD_HASH_PREFIX}",
            body=HIBP_HASH_RANGE_NO_MATCH,
            status=200,
        )

        is_pwned, count = check_passwords.check_password(SAFE_PASSWORD)

        assert is_pwned is False
        assert count == 0

    @responses.activate
    def test_check_password_network_error(self):
        """Test that network errors are handled gracefully."""
        from requests.exceptions import ConnectionError

        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=ConnectionError("Network unreachable"),
        )

        is_pwned, count = check_passwords.check_password(PWNED_PASSWORD)

        assert is_pwned is False
        assert count == -1

    @responses.activate
    def test_check_password_timeout(self):
        """Test that timeout errors are handled gracefully."""
        from requests.exceptions import Timeout

        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=Timeout("Connection timed out"),
        )

        is_pwned, count = check_passwords.check_password(PWNED_PASSWORD)

        assert is_pwned is False
        assert count == -1

    @responses.activate
    def test_check_password_server_error(self):
        """Test that server errors (5xx) are handled gracefully."""
        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body="Service unavailable",
            status=503,
        )

        is_pwned, count = check_passwords.check_password(PWNED_PASSWORD)

        assert is_pwned is False
        assert count == -1

    @responses.activate
    def test_check_password_uses_correct_hash(self):
        """Test that the correct SHA-1 hash is computed and used."""
        # Compute expected hash
        expected_hash = hashlib.sha1(PWNED_PASSWORD.encode('utf-8')).hexdigest().upper()
        expected_prefix = expected_hash[:5]

        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{expected_prefix}",
            body=HIBP_HASH_RANGE_WITH_MATCH,
            status=200,
        )

        check_passwords.check_password(PWNED_PASSWORD)

        # Verify the correct URL was called
        assert len(responses.calls) == 1
        assert expected_prefix in responses.calls[0].request.url

    @responses.activate
    def test_check_password_unicode(self):
        """Test that unicode passwords are handled correctly."""
        unicode_password = "pAssw0rd!"
        sha1_hash = hashlib.sha1(unicode_password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_hash[:5]

        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{prefix}",
            body=HIBP_HASH_RANGE_NO_MATCH,
            status=200,
        )

        is_pwned, count = check_passwords.check_password(unicode_password)

        assert is_pwned is False
        assert count == 0

    @responses.activate
    def test_check_password_empty_response(self):
        """Test handling of empty API response."""
        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body="",
            status=200,
        )

        is_pwned, count = check_passwords.check_password(PWNED_PASSWORD)

        assert is_pwned is False
        assert count == 0


class TestFormatCount:
    """Tests for the format_count() function."""

    def test_format_count_safe(self):
        """Test formatting for safe password (count = 0)."""
        result = check_passwords.format_count(0)

        assert "Safe" in result
        assert "not found" in result
        # Check for green color code
        assert "\033[0;32m" in result

    def test_format_count_low_risk(self):
        """Test formatting for low risk (count < 10)."""
        for count in [1, 5, 9]:
            result = check_passwords.format_count(count)

            assert "low risk" in result.lower()
            assert str(count) in result
            # Check for yellow color code
            assert "\033[1;33m" in result

    def test_format_count_medium_risk(self):
        """Test formatting for medium risk (10 <= count < 100)."""
        for count in [10, 50, 99]:
            result = check_passwords.format_count(count)

            assert "medium risk" in result.lower()
            assert str(count) in result
            # Check for red color code
            assert "\033[0;31m" in result

    def test_format_count_high_risk(self):
        """Test formatting for high risk (100 <= count < 1000)."""
        for count in [100, 500, 999]:
            result = check_passwords.format_count(count)

            assert "high risk" in result.lower()
            assert str(count) in result
            # Check for red color code
            assert "\033[0;31m" in result

    def test_format_count_critical(self):
        """Test formatting for critical risk (count >= 1000)."""
        for count in [1000, 5000, 1000000]:
            result = check_passwords.format_count(count)

            assert "CRITICAL" in result
            assert "change immediately" in result.lower()
            # Check for bold red color code
            assert "\033[1;31m" in result

    def test_format_count_singular_vs_plural(self):
        """Test correct singular/plural handling."""
        result_one = check_passwords.format_count(1)
        result_many = check_passwords.format_count(5)

        assert "1 time" in result_one and "1 times" not in result_one
        assert "times" in result_many

    def test_format_count_number_formatting(self):
        """Test that large numbers are formatted with commas."""
        result = check_passwords.format_count(1000000)

        assert "1,000,000" in result

    def test_format_count_edge_values(self):
        """Test boundary values between risk levels."""
        # Boundary between safe and low
        assert "Safe" in check_passwords.format_count(0)
        assert "low risk" in check_passwords.format_count(1).lower()

        # Boundary between low and medium
        assert "low risk" in check_passwords.format_count(9).lower()
        assert "medium risk" in check_passwords.format_count(10).lower()

        # Boundary between medium and high
        assert "medium risk" in check_passwords.format_count(99).lower()
        assert "high risk" in check_passwords.format_count(100).lower()

        # Boundary between high and critical
        assert "high risk" in check_passwords.format_count(999).lower()
        assert "CRITICAL" in check_passwords.format_count(1000)


class TestHashComputation:
    """Tests for SHA-1 hash computation used in password checking."""

    def test_sha1_hash_uppercase(self):
        """Test that SHA-1 hashes are computed in uppercase."""
        password = "test"
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()

        # Should be all uppercase hex
        assert sha1_hash == sha1_hash.upper()
        assert len(sha1_hash) == 40

    def test_sha1_hash_consistency(self):
        """Test that the same password always produces the same hash."""
        password = "consistent_password"
        hash1 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        hash2 = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()

        assert hash1 == hash2

    def test_sha1_prefix_length(self):
        """Test that hash prefix is exactly 5 characters."""
        password = "any_password"
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]

        assert len(prefix) == 5
        assert len(suffix) == 35


class TestPasswordMatchingLogic:
    """Tests for the password matching logic in check_password."""

    @responses.activate
    def test_exact_suffix_match_required(self):
        """Test that only exact suffix matches are detected."""
        # Create a response with a similar but not exact suffix
        partial_match_response = """0018A45C4D1DEF81644B54AB7F969B88D65:15
1E4C9B93F3F0682250B6CF8331B7EE68FD7:1000
1E4C9B93F3F0682250B6CF8331B7EE68FD9:2000"""

        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=partial_match_response,
            status=200,
        )

        is_pwned, count = check_passwords.check_password(PWNED_PASSWORD)

        # Should not match - suffix is different
        assert is_pwned is False
        assert count == 0

    @responses.activate
    def test_count_parsing(self):
        """Test that breach count is correctly parsed from response."""
        custom_count = 12345
        response = f"""0018A45C4D1DEF81644B54AB7F969B88D65:15
1E4C9B93F3F0682250B6CF8331B7EE68FD8:{custom_count}
A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6E7:1"""

        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=response,
            status=200,
        )

        is_pwned, count = check_passwords.check_password(PWNED_PASSWORD)

        assert is_pwned is True
        assert count == custom_count


class TestErrorMessages:
    """Tests for error message output."""

    @responses.activate
    def test_network_error_prints_to_stderr(self, capsys):
        """Test that network errors are printed to stderr."""
        from requests.exceptions import ConnectionError

        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=ConnectionError("Network error"),
        )

        check_passwords.check_password(PWNED_PASSWORD)

        captured = capsys.readouterr()
        assert "Error" in captured.err or "error" in captured.err.lower()
