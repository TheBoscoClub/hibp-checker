"""Unit tests for hibp_comprehensive_checker.py module.

Tests the comprehensive HIBP checker including:
- HIBPChecker class initialization
- Breach checking methods
- Password checking methods
- Stealer logs checking
- Paste checking
- Report generation
- Risk assessment
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import responses

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from hibp_comprehensive_checker import HIBPChecker

from tests.fixtures.mock_responses import (
    HIBP_HASH_RANGE_WITH_MATCH,
    HIBP_HASH_RANGE_NO_MATCH,
    HIBP_BREACH_RESPONSE,
    HIBP_PASTE_RESPONSE,
    HIBP_STEALER_LOGS_RESPONSE,
    HIBP_ERROR_401,
)
from tests.fixtures.sample_data import (
    PWNED_PASSWORD,
    PWNED_PASSWORD_HASH_PREFIX,
    PWNED_PASSWORD_COUNT,
    SAFE_PASSWORD,
    SAFE_PASSWORD_HASH_PREFIX,
    TEST_EMAIL,
    TEST_EMAILS,
)


class TestHIBPCheckerInit:
    """Tests for HIBPChecker initialization."""

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        checker = HIBPChecker(api_key="test-api-key")

        assert checker.api_key == "test-api-key"
        assert "hibp-api-key" in checker.headers

    def test_init_verbose_mode(self):
        """Test initialization with verbose mode."""
        checker = HIBPChecker(api_key="key", verbose=True)

        assert checker.verbose is True

    def test_init_non_verbose_mode(self):
        """Test initialization without verbose mode."""
        checker = HIBPChecker(api_key="key", verbose=False)

        assert checker.verbose is False

    def test_init_sets_base_url(self):
        """Test that base URL is set correctly."""
        checker = HIBPChecker(api_key="key")

        assert checker.base_url == "https://haveibeenpwned.com/api/v3"

    def test_init_sets_pwned_passwords_url(self):
        """Test that pwned passwords URL is set correctly."""
        checker = HIBPChecker(api_key="key")

        assert checker.pwned_pw_url == "https://api.pwnedpasswords.com/range"

    def test_init_sets_rate_limit_delay(self):
        """Test that rate limit delay is configured."""
        checker = HIBPChecker(api_key="key")

        assert checker.rate_limit_delay > 0


class TestHIBPCheckerLog:
    """Tests for the log() method."""

    def test_log_verbose_info(self, capsys):
        """Test logging INFO messages in verbose mode."""
        checker = HIBPChecker(api_key="key", verbose=True)

        checker.log("Test message", "INFO")

        captured = capsys.readouterr()
        assert "Test message" in captured.out
        assert "INFO" in captured.out

    def test_log_non_verbose_info(self, capsys):
        """Test that INFO is suppressed in non-verbose mode."""
        checker = HIBPChecker(api_key="key", verbose=False)

        checker.log("Test message", "INFO")

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_log_non_verbose_error(self, capsys):
        """Test that ERROR is always shown."""
        checker = HIBPChecker(api_key="key", verbose=False)

        checker.log("Error message", "ERROR")

        captured = capsys.readouterr()
        assert "Error message" in captured.out

    def test_log_includes_timestamp(self, capsys):
        """Test that log includes timestamp."""
        checker = HIBPChecker(api_key="key", verbose=True)

        checker.log("Test", "INFO")

        captured = capsys.readouterr()
        # Timestamp format: YYYY-MM-DD HH:MM:SS
        assert "[20" in captured.out  # Year starts with 20xx


class TestMakeRequest:
    """Tests for the make_request() method."""

    @responses.activate
    def test_make_request_success(self):
        """Test successful API request."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            "https://haveibeenpwned.com/api/v3/test-endpoint",
            json={"data": "test"},
            status=200,
        )

        result = checker.make_request("test-endpoint")

        assert result == {"data": "test"}

    @responses.activate
    def test_make_request_404(self):
        """Test handling of 404 response (not found)."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            "https://haveibeenpwned.com/api/v3/test-endpoint",
            status=404,
        )

        result = checker.make_request("test-endpoint")

        assert result is None

    @responses.activate
    def test_make_request_401(self, capsys):
        """Test handling of 401 unauthorized."""
        checker = HIBPChecker(api_key="bad-key")

        responses.add(
            responses.GET,
            "https://haveibeenpwned.com/api/v3/test-endpoint",
            json=HIBP_ERROR_401,
            status=401,
        )

        result = checker.make_request("test-endpoint")

        assert result is None
        captured = capsys.readouterr()
        assert "401" in captured.out or "error" in captured.out.lower()

    @responses.activate
    def test_make_request_includes_headers(self):
        """Test that request includes required headers."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            "https://haveibeenpwned.com/api/v3/test-endpoint",
            json={},
            status=200,
        )

        checker.make_request("test-endpoint")

        request = responses.calls[0].request
        assert request.headers["hibp-api-key"] == "test-key"
        assert "user-agent" in [h.lower() for h in request.headers.keys()]


class TestCheckBreaches:
    """Tests for the check_breaches() method."""

    @responses.activate
    def test_check_breaches_found(self):
        """Test checking an email with breaches."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{TEST_EMAIL}",
            json=HIBP_BREACH_RESPONSE,
            status=200,
        )

        result = checker.check_breaches(TEST_EMAIL)

        assert result["email"] == TEST_EMAIL
        assert result["breach_count"] == len(HIBP_BREACH_RESPONSE)
        assert len(result["breaches"]) > 0

    @responses.activate
    def test_check_breaches_not_found(self):
        """Test checking an email with no breaches."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{TEST_EMAIL}",
            status=404,
        )

        result = checker.check_breaches(TEST_EMAIL)

        assert result["email"] == TEST_EMAIL
        assert result["breach_count"] == 0
        assert result["breaches"] == []

    @responses.activate
    def test_check_breaches_password_exposed(self):
        """Test that password exposures are detected."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{TEST_EMAIL}",
            json=HIBP_BREACH_RESPONSE,
            status=200,
        )

        result = checker.check_breaches(TEST_EMAIL)

        # HIBP_BREACH_RESPONSE has breaches with "Passwords" in DataClasses
        assert len(result["password_exposed"]) > 0

    @responses.activate
    def test_check_breaches_stealer_logs(self):
        """Test that stealer logs are detected."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{TEST_EMAIL}",
            json=HIBP_BREACH_RESPONSE,
            status=200,
        )

        result = checker.check_breaches(TEST_EMAIL)

        # HIBP_BREACH_RESPONSE has RedLineStealer with IsStealerLog=True
        assert len(result["stealer_logs"]) > 0

    @responses.activate
    def test_check_breaches_verified_unverified(self):
        """Test categorization of verified vs unverified breaches."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{TEST_EMAIL}",
            json=HIBP_BREACH_RESPONSE,
            status=200,
        )

        result = checker.check_breaches(TEST_EMAIL)

        # Should have some verified breaches
        assert len(result["verified_breaches"]) > 0
        # Collection1 is unverified
        assert "Collection1" in result["unverified_breaches"]

    @responses.activate
    def test_check_breaches_sensitive(self):
        """Test detection of sensitive breaches."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{TEST_EMAIL}",
            json=HIBP_BREACH_RESPONSE,
            status=200,
        )

        result = checker.check_breaches(TEST_EMAIL)

        # AdultFriendFinder is sensitive
        assert "AdultFriendFinder" in result["sensitive_breaches"]

    @responses.activate
    def test_check_breaches_data_classes(self):
        """Test that data classes are collected."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{TEST_EMAIL}",
            json=HIBP_BREACH_RESPONSE,
            status=200,
        )

        result = checker.check_breaches(TEST_EMAIL)

        assert "Passwords" in result["data_classes"]
        assert "Email addresses" in result["data_classes"]


class TestAnalyzePasswordExposure:
    """Tests for the _analyze_password_exposure() method."""

    def test_analyze_plaintext(self):
        """Test detection of plaintext password exposure."""
        checker = HIBPChecker(api_key="key")
        breach = {"Description": "Passwords were stored in plain text"}

        result = checker._analyze_password_exposure(breach)

        assert result == "plaintext"

    def test_analyze_bcrypt(self):
        """Test detection of bcrypt hashed passwords."""
        checker = HIBPChecker(api_key="key")
        breach = {"Description": "Passwords were hashed using bcrypt"}

        result = checker._analyze_password_exposure(breach)

        assert result == "bcrypt_hash"

    def test_analyze_sha1(self):
        """Test detection of SHA-1 hashed passwords."""
        checker = HIBPChecker(api_key="key")
        breach = {"Description": "Passwords were stored as SHA-1 hashes"}

        result = checker._analyze_password_exposure(breach)

        assert result == "sha1_hash"

    def test_analyze_md5(self):
        """Test detection of MD5 hashed passwords."""
        checker = HIBPChecker(api_key="key")
        breach = {"Description": "Password hashes were MD5"}

        result = checker._analyze_password_exposure(breach)

        assert result == "md5_hash"

    def test_analyze_unknown(self):
        """Test handling of unknown password storage."""
        checker = HIBPChecker(api_key="key")
        breach = {"Description": "User data was exposed"}

        result = checker._analyze_password_exposure(breach)

        assert result == "unknown"


class TestCheckStealerLogs:
    """Tests for the check_stealer_logs() method."""

    @responses.activate
    def test_check_stealer_logs_found(self):
        """Test checking stealer logs with results."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/stealerlogsbyemail/{TEST_EMAIL}",
            json=HIBP_STEALER_LOGS_RESPONSE,
            status=200,
        )

        result = checker.check_stealer_logs(TEST_EMAIL)

        assert result["email"] == TEST_EMAIL
        assert result["count"] == len(HIBP_STEALER_LOGS_RESPONSE)
        assert len(result["compromised_sites"]) > 0

    @responses.activate
    def test_check_stealer_logs_not_found(self):
        """Test checking stealer logs with no results."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/stealerlogsbyemail/{TEST_EMAIL}",
            status=404,
        )

        result = checker.check_stealer_logs(TEST_EMAIL)

        assert result["count"] == 0
        assert result["compromised_sites"] == []

    @responses.activate
    def test_check_stealer_logs_critical_sites(self):
        """Test identification of critical sites."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/stealerlogsbyemail/{TEST_EMAIL}",
            json=HIBP_STEALER_LOGS_RESPONSE,
            status=200,
        )

        result = checker.check_stealer_logs(TEST_EMAIL)

        # HIBP_STEALER_LOGS_RESPONSE includes amazon, paypal, google, etc.
        assert len(result["critical"]) > 0
        assert any("amazon" in site.lower() for site in result["critical"])


class TestIdentifyCriticalSites:
    """Tests for the _identify_critical_sites() method."""

    def test_identify_banking_sites(self):
        """Test identification of banking sites."""
        checker = HIBPChecker(api_key="key")
        domains = ["bankofamerica.com", "random.com"]

        critical = checker._identify_critical_sites(domains)

        assert "bankofamerica.com" in critical
        assert "random.com" not in critical

    def test_identify_payment_sites(self):
        """Test identification of payment sites."""
        checker = HIBPChecker(api_key="key")
        domains = ["paypal.com", "stripe.com"]

        critical = checker._identify_critical_sites(domains)

        assert "paypal.com" in critical
        assert "stripe.com" in critical

    def test_identify_cloud_providers(self):
        """Test identification of cloud provider sites."""
        checker = HIBPChecker(api_key="key")
        domains = ["aws.amazon.com", "azure.microsoft.com"]

        critical = checker._identify_critical_sites(domains)

        assert len(critical) >= 1


class TestCheckPastes:
    """Tests for the check_pastes() method."""

    @responses.activate
    def test_check_pastes_found(self):
        """Test checking pastes with results."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/pasteaccount/{TEST_EMAIL}",
            json=HIBP_PASTE_RESPONSE,
            status=200,
        )

        result = checker.check_pastes(TEST_EMAIL)

        assert result["email"] == TEST_EMAIL
        assert result["count"] == len(HIBP_PASTE_RESPONSE)
        assert len(result["pastes"]) > 0

    @responses.activate
    def test_check_pastes_not_found(self):
        """Test checking pastes with no results."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/pasteaccount/{TEST_EMAIL}",
            status=404,
        )

        result = checker.check_pastes(TEST_EMAIL)

        assert result["count"] == 0
        assert result["pastes"] == []

    @responses.activate
    def test_check_pastes_sources(self):
        """Test that paste sources are extracted."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/pasteaccount/{TEST_EMAIL}",
            json=HIBP_PASTE_RESPONSE,
            status=200,
        )

        result = checker.check_pastes(TEST_EMAIL)

        assert "Pastebin" in result["sources"]


class TestCheckPassword:
    """Tests for the check_password() method."""

    @responses.activate
    def test_check_password_found(self):
        """Test checking a pwned password."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=HIBP_HASH_RANGE_WITH_MATCH,
            status=200,
        )

        result = checker.check_password(PWNED_PASSWORD)

        assert result["found"] is True
        assert result["appearances"] == PWNED_PASSWORD_COUNT
        assert result["risk_level"] == "critical"

    @responses.activate
    def test_check_password_not_found(self):
        """Test checking a safe password."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{SAFE_PASSWORD_HASH_PREFIX}",
            body=HIBP_HASH_RANGE_NO_MATCH,
            status=200,
        )

        result = checker.check_password(SAFE_PASSWORD)

        assert result["found"] is False
        assert result["appearances"] == 0
        assert result["risk_level"] == "safe"

    @responses.activate
    def test_check_password_hash_truncated(self):
        """Test that returned hash is truncated for security."""
        checker = HIBPChecker(api_key="test-key")

        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=HIBP_HASH_RANGE_WITH_MATCH,
            status=200,
        )

        result = checker.check_password(PWNED_PASSWORD)

        # Hash should be truncated with "..."
        assert result["password_hash"].endswith("...")
        assert len(result["password_hash"]) < 40


class TestAssessPasswordRisk:
    """Tests for the _assess_password_risk() method."""

    def test_risk_safe(self):
        """Test safe risk level."""
        checker = HIBPChecker(api_key="key")

        assert checker._assess_password_risk(0) == "safe"

    def test_risk_low(self):
        """Test low risk level."""
        checker = HIBPChecker(api_key="key")

        assert checker._assess_password_risk(5) == "low"
        assert checker._assess_password_risk(9) == "low"

    def test_risk_medium(self):
        """Test medium risk level."""
        checker = HIBPChecker(api_key="key")

        assert checker._assess_password_risk(10) == "medium"
        assert checker._assess_password_risk(99) == "medium"

    def test_risk_high(self):
        """Test high risk level."""
        checker = HIBPChecker(api_key="key")

        assert checker._assess_password_risk(100) == "high"
        assert checker._assess_password_risk(999) == "high"

    def test_risk_critical(self):
        """Test critical risk level."""
        checker = HIBPChecker(api_key="key")

        assert checker._assess_password_risk(1000) == "critical"
        assert checker._assess_password_risk(1000000) == "critical"


class TestComprehensiveCheck:
    """Tests for the comprehensive_check() method."""

    @responses.activate
    def test_comprehensive_check_emails(self):
        """Test comprehensive check with emails."""
        checker = HIBPChecker(api_key="test-key")

        # Mock all endpoints for each email
        for email in TEST_EMAILS[:1]:
            responses.add(
                responses.GET,
                f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                json=HIBP_BREACH_RESPONSE,
                status=200,
            )
            responses.add(
                responses.GET,
                f"https://haveibeenpwned.com/api/v3/stealerlogsbyemail/{email}",
                json=HIBP_STEALER_LOGS_RESPONSE,
                status=200,
            )
            responses.add(
                responses.GET,
                f"https://haveibeenpwned.com/api/v3/pasteaccount/{email}",
                json=HIBP_PASTE_RESPONSE,
                status=200,
            )

        results = checker.comprehensive_check(TEST_EMAILS[:1])

        assert "scan_date" in results
        assert "summary" in results
        assert len(results["emails_checked"]) == 1

    @responses.activate
    def test_comprehensive_check_with_passwords(self):
        """Test comprehensive check including passwords."""
        checker = HIBPChecker(api_key="test-key")

        # Mock email endpoints
        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{TEST_EMAIL}",
            status=404,
        )
        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/stealerlogsbyemail/{TEST_EMAIL}",
            status=404,
        )
        responses.add(
            responses.GET,
            f"https://haveibeenpwned.com/api/v3/pasteaccount/{TEST_EMAIL}",
            status=404,
        )

        # Mock password endpoint
        responses.add(
            responses.GET,
            f"https://api.pwnedpasswords.com/range/{PWNED_PASSWORD_HASH_PREFIX}",
            body=HIBP_HASH_RANGE_WITH_MATCH,
            status=200,
        )

        results = checker.comprehensive_check([TEST_EMAIL], [PWNED_PASSWORD])

        assert len(results["passwords_checked"]) == 1
        assert results["passwords_checked"][0]["found"] is True


class TestGenerateReport:
    """Tests for the generate_report() method."""

    def test_generate_report_json(self, temp_dir, monkeypatch):
        """Test generating JSON report."""
        monkeypatch.chdir(temp_dir)

        checker = HIBPChecker(api_key="key")
        results = {
            "scan_date": datetime.now().isoformat(),
            "summary": {"total_breaches": 0},
            "emails_checked": []
        }

        filename = checker.generate_report(results, "json")

        assert filename.endswith(".json")
        assert Path(filename).exists()

        with open(filename) as f:
            data = json.load(f)
            assert "scan_date" in data

    def test_generate_report_csv(self, temp_dir, monkeypatch):
        """Test generating CSV report."""
        monkeypatch.chdir(temp_dir)

        checker = HIBPChecker(api_key="key")
        results = {
            "scan_date": datetime.now().isoformat(),
            "summary": {"total_breaches": 0},
            "emails_checked": [
                {
                    "email": TEST_EMAIL,
                    "breaches": {"breach_count": 0, "password_exposed": []},
                    "stealer_logs": {"count": 0, "critical": []},
                    "pastes": {"count": 0}
                }
            ]
        }

        filename = checker.generate_report(results, "csv")

        assert filename.endswith(".csv")
        assert Path(filename).exists()

    def test_generate_report_text(self, temp_dir, monkeypatch):
        """Test generating text report."""
        monkeypatch.chdir(temp_dir)

        checker = HIBPChecker(api_key="key")
        results = {
            "scan_date": datetime.now().isoformat(),
            "summary": {"total_breaches": 5, "password_exposures": 2},
            "emails_checked": [
                {
                    "email": TEST_EMAIL,
                    "breaches": {
                        "breach_count": 5,
                        "password_exposed": [
                            {"title": "Test", "date": "2024-01-01", "password_type": "plaintext"}
                        ]
                    },
                    "stealer_logs": {"count": 2, "compromised_sites": ["test.com"], "critical": ["bank.com"]},
                    "pastes": {"count": 1, "sources": ["Pastebin"]}
                }
            ]
        }

        filename = checker.generate_report(results, "text")

        assert filename.endswith(".txt")
        assert Path(filename).exists()

        content = Path(filename).read_text()
        assert "HIBP COMPREHENSIVE BREACH REPORT" in content
        assert TEST_EMAIL in content
