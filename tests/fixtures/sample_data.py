"""Sample test data for HIBP Project tests.

This module contains sample data structures that simulate real-world inputs:
- Bitwarden vault exports
- Test passwords (safe and pwned)
- Email addresses for testing
- Various edge case data
"""

import hashlib

# =============================================================================
# Test Passwords
# =============================================================================

# A known pwned password: "password"
# SHA1: 5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8
PWNED_PASSWORD = "password"
PWNED_PASSWORD_SHA1 = "5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8"
PWNED_PASSWORD_HASH_PREFIX = "5BAA6"
PWNED_PASSWORD_HASH_SUFFIX = "1E4C9B93F3F0682250B6CF8331B7EE68FD8"
PWNED_PASSWORD_COUNT = 10434471

# A safe password (extremely unlikely to be in breaches)
SAFE_PASSWORD = "Xk9!mN2@pQ7#rT4$vW6%yZ8^aB1&cD3*eF5(gH0)"
# SHA1 is required by HIBP API protocol, not used for security purposes
SAFE_PASSWORD_SHA1 = hashlib.sha1(SAFE_PASSWORD.encode('utf-8'), usedforsecurity=False).hexdigest().upper()
SAFE_PASSWORD_HASH_PREFIX = SAFE_PASSWORD_SHA1[:5]
SAFE_PASSWORD_HASH_SUFFIX = SAFE_PASSWORD_SHA1[5:]

# Various weak passwords for testing different count levels
WEAK_PASSWORDS = {
    "123456": 42542807,      # Critical
    "qwerty": 4322639,       # Critical
    "letmein": 71093,        # High
    "admin": 150000,         # High
    "welcome": 318674,       # High
}

# Empty and edge case passwords
EMPTY_PASSWORD = ""
WHITESPACE_PASSWORD = "   "
UNICODE_PASSWORD = "pAssw0rd!@#$%^&*()"
LONG_PASSWORD = "a" * 1000


# =============================================================================
# Test Email Addresses
# =============================================================================

TEST_EMAIL = "test@example.com"
TEST_EMAIL_BREACHED = "breached@test.com"
TEST_EMAIL_CLEAN = "clean@test.com"

TEST_EMAILS = [
    "user1@example.com",
    "user2@example.com",
    "admin@company.com",
]


# =============================================================================
# Bitwarden Export Data
# =============================================================================

SAMPLE_BITWARDEN_ITEMS = [
    {
        "id": "item-1-uuid",
        "organizationId": None,
        "folderId": None,
        "type": 1,  # Login type
        "name": "Example Site",
        "notes": None,
        "favorite": False,
        "login": {
            "username": "testuser",
            "password": PWNED_PASSWORD,  # This is pwned
            "totp": None,
            "uris": [
                {"uri": "https://example.com", "match": None}
            ]
        },
        "collectionIds": None,
        "revisionDate": "2024-01-15T10:30:00.000Z"
    },
    {
        "id": "item-2-uuid",
        "organizationId": None,
        "folderId": None,
        "type": 1,
        "name": "Secure Bank",
        "notes": "Primary banking account",
        "favorite": True,
        "login": {
            "username": "bankuser@email.com",
            "password": SAFE_PASSWORD,  # This is safe
            "totp": "JBSWY3DPEHPK3PXP",
            "uris": [
                {"uri": "https://securebank.com/login", "match": None}
            ]
        },
        "collectionIds": None,
        "revisionDate": "2024-01-10T08:00:00.000Z"
    },
    {
        "id": "item-3-uuid",
        "organizationId": None,
        "folderId": None,
        "type": 1,
        "name": "Social Media",
        "notes": None,
        "favorite": False,
        "login": {
            "username": "socialuser",
            "password": "123456",  # Critical - very common
            "totp": None,
            "uris": [
                {"uri": "https://social.example.com", "match": None}
            ]
        },
        "collectionIds": None,
        "revisionDate": "2024-01-12T15:45:00.000Z"
    },
    {
        "id": "item-4-uuid",
        "organizationId": None,
        "folderId": None,
        "type": 1,
        "name": "Work Email",
        "notes": None,
        "favorite": False,
        "login": {
            "username": "worker@company.com",
            "password": "qwerty",  # Critical
            "totp": None,
            "uris": []  # No URI
        },
        "collectionIds": None,
        "revisionDate": "2024-01-05T12:00:00.000Z"
    },
    {
        "id": "item-5-uuid",
        "organizationId": None,
        "folderId": None,
        "type": 1,
        "name": "Empty Password Entry",
        "notes": None,
        "favorite": False,
        "login": {
            "username": "nopassword",
            "password": "",  # Empty password
            "totp": None,
            "uris": []
        },
        "collectionIds": None,
        "revisionDate": "2024-01-01T00:00:00.000Z"
    }
]

# Full Bitwarden export format (as exported from Bitwarden)
SAMPLE_BITWARDEN_EXPORT = {
    "encrypted": False,
    "folders": [
        {"id": "folder-1-uuid", "name": "Personal"},
        {"id": "folder-2-uuid", "name": "Work"}
    ],
    "items": SAMPLE_BITWARDEN_ITEMS + [
        # Add a non-login item to test filtering
        {
            "id": "item-6-uuid",
            "organizationId": None,
            "folderId": None,
            "type": 2,  # Secure Note type
            "name": "Secret Notes",
            "notes": "These are secret notes",
            "favorite": False,
            "secureNote": {"type": 0},
            "collectionIds": None,
            "revisionDate": "2024-01-08T09:00:00.000Z"
        },
        # Card item
        {
            "id": "item-7-uuid",
            "organizationId": None,
            "folderId": None,
            "type": 3,  # Card type
            "name": "Credit Card",
            "notes": None,
            "favorite": False,
            "card": {
                "cardholderName": "Test User",
                "brand": "Visa",
                "number": "4111111111111111",
                "expMonth": "12",
                "expYear": "2025",
                "code": "123"
            },
            "collectionIds": None,
            "revisionDate": "2024-01-03T11:30:00.000Z"
        }
    ]
}

# Bitwarden export with only safe passwords
SAMPLE_BITWARDEN_EXPORT_SAFE = {
    "encrypted": False,
    "folders": [],
    "items": [
        {
            "id": "safe-item-1",
            "type": 1,
            "name": "Safe Site 1",
            "login": {
                "username": "user1",
                "password": SAFE_PASSWORD,
                "uris": [{"uri": "https://safe1.com"}]
            },
            "revisionDate": "2024-01-15T10:00:00.000Z"
        },
        {
            "id": "safe-item-2",
            "type": 1,
            "name": "Safe Site 2",
            "login": {
                "username": "user2",
                "password": "AnotherVerySecurePassword!@#$%^789",
                "uris": [{"uri": "https://safe2.com"}]
            },
            "revisionDate": "2024-01-15T11:00:00.000Z"
        }
    ]
}

# Empty Bitwarden export
SAMPLE_BITWARDEN_EXPORT_EMPTY = {
    "encrypted": False,
    "folders": [],
    "items": []
}

# Bitwarden export with only non-login items
SAMPLE_BITWARDEN_EXPORT_NO_LOGINS = {
    "encrypted": False,
    "folders": [],
    "items": [
        {
            "id": "note-item",
            "type": 2,
            "name": "Just a Note",
            "notes": "Some notes here",
            "secureNote": {"type": 0}
        }
    ]
}


# =============================================================================
# Report Data
# =============================================================================

SAMPLE_REPORT_SUMMARY = {
    "total": 5,
    "safe": 2,
    "compromised": 3,
    "errors": 0,
    "critical_count": 2,
    "high_count": 0,
}

SAMPLE_CHECK_RESULTS = [
    {
        "name": "Example Site",
        "username": "testuser",
        "uri": "https://example.com",
        "status": "compromised",
        "risk_level": "critical",
        "breach_count": PWNED_PASSWORD_COUNT,
        "error": None
    },
    {
        "name": "Secure Bank",
        "username": "bankuser@email.com",
        "uri": "https://securebank.com/login",
        "status": "safe",
        "risk_level": "safe",
        "breach_count": 0,
        "error": None
    },
    {
        "name": "Social Media",
        "username": "socialuser",
        "uri": "https://social.example.com",
        "status": "compromised",
        "risk_level": "critical",
        "breach_count": 42542807,
        "error": None
    }
]


# =============================================================================
# JSON Input/Output Formats
# =============================================================================

# JSON output from bw-hibp-stream.py
SAMPLE_STREAM_JSON_OUTPUT = {
    "generated": "2024-01-15T10:30:00.000000",
    "summary": {
        "total": 5,
        "safe": 2,
        "compromised": 2,
        "errors": 1,
        "critical_count": 1,
        "high_count": 1
    },
    "items": [
        {
            "name": "Example Site",
            "username": "testuser",
            "uri": "https://example.com",
            "status": "compromised",
            "risk_level": "critical",
            "breach_count": 10434471,
            "error": None
        },
        {
            "name": "Secure Bank",
            "username": "bankuser@email.com",
            "uri": "https://securebank.com/login",
            "status": "safe",
            "risk_level": "safe",
            "breach_count": 0,
            "error": None
        },
        {
            "name": "Work Portal",
            "username": "worker",
            "uri": "https://work.example.com",
            "status": "compromised",
            "risk_level": "high",
            "breach_count": 500,
            "error": None
        },
        {
            "name": "Old Account",
            "username": "old_user",
            "uri": "",
            "status": "error",
            "risk_level": "unknown",
            "breach_count": -1,
            "error": "Connection timeout"
        },
        {
            "name": "Another Safe",
            "username": "safe_user",
            "uri": "https://another.com",
            "status": "safe",
            "risk_level": "safe",
            "breach_count": 0,
            "error": None
        }
    ]
}


# =============================================================================
# Edge Cases
# =============================================================================

# Malformed JSON
MALFORMED_JSON = '{"items": [{"name": "test"'

# JSON with unexpected structure
UNEXPECTED_JSON_STRUCTURE = {
    "data": {
        "entries": []
    }
}

# Large item count for pagination/performance testing
def generate_large_bitwarden_export(num_items: int = 100) -> dict:
    """Generate a large Bitwarden export for performance testing.

    Args:
        num_items: Number of login items to generate.

    Returns:
        dict: Bitwarden export with specified number of items.
    """
    items = []
    for i in range(num_items):
        items.append({
            "id": f"item-{i}-uuid",
            "type": 1,
            "name": f"Test Site {i}",
            "login": {
                "username": f"user{i}@test.com",
                "password": f"Password{i}!",
                "uris": [{"uri": f"https://site{i}.example.com"}]
            },
            "revisionDate": "2024-01-15T10:00:00.000Z"
        })

    return {
        "encrypted": False,
        "folders": [],
        "items": items
    }
