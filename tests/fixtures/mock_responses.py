"""Mock HIBP API responses for testing.

This module contains realistic mock responses that match the actual HIBP API
response formats for:
- Pwned Passwords API (k-anonymity hash range responses)
- Breach API (breached accounts)
- Paste API (paste exposures)
- Stealer Logs API
"""

# =============================================================================
# Pwned Passwords API Mock Responses
# =============================================================================

# Response format: SHA1_SUFFIX:COUNT (one per line)
# This simulates the k-anonymity response from https://api.pwnedpasswords.com/range/{prefix}

# The password "password" has SHA1 hash: 5BAA61E4C9B93F3F0682250B6CF8331B7EE68FD8
# Prefix: 5BAA6, Suffix: 1E4C9B93F3F0682250B6CF8331B7EE68FD8

HIBP_HASH_RANGE_WITH_MATCH = """0018A45C4D1DEF81644B54AB7F969B88D65:15
003D68EB55068C33ACE09247EE4C639306B:3
012C192B2F16F82EA0EB9EF18D9D539B0DD:2
01330C689E5D64F660D6947A93AD634EF8F:2
02FC2E40E77F8E3C7D83D09B3C8D119C5FF:1
1E4C9B93F3F0682250B6CF8331B7EE68FD8:10434471
21BD10018A45C4D1DEF81644B54AB7F969B:4
3D2D7CABBF2B79F9D1F1A8D5E5C23E4A123:1
4A5E5C23E4D1F1A8D5E5C23E4A123B2C3D:8
5B6C7D8E9F0A1B2C3D4E5F6A7B8C9D0E1F:42
6C7D8E9F0A1B2C3D4E5F6A7B8C9D0E1F2A:156
7D8E9F0A1B2C3D4E5F6A7B8C9D0E1F2A3B:7
8E9F0A1B2C3D4E5F6A7B8C9D0E1F2A3B4C:2341
9F0A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D:99
A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6E7:1"""

# Response when password hash suffix is NOT found
HIBP_HASH_RANGE_NO_MATCH = """0018A45C4D1DEF81644B54AB7F969B88D65:15
003D68EB55068C33ACE09247EE4C639306B:3
012C192B2F16F82EA0EB9EF18D9D539B0DD:2
01330C689E5D64F660D6947A93AD634EF8F:2
02FC2E40E77F8E3C7D83D09B3C8D119C5FF:1
21BD10018A45C4D1DEF81644B54AB7F969B:4
3D2D7CABBF2B79F9D1F1A8D5E5C23E4A123:1
4A5E5C23E4D1F1A8D5E5C23E4A123B2C3D:8
5B6C7D8E9F0A1B2C3D4E5F6A7B8C9D0E1F:42
6C7D8E9F0A1B2C3D4E5F6A7B8C9D0E1F2A:156
7D8E9F0A1B2C3D4E5F6A7B8C9D0E1F2A3B:7
8E9F0A1B2C3D4E5F6A7B8C9D0E1F2A3B4C:2341
9F0A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D:99
A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6E7:1"""

# Empty response (no hashes in this range - very rare)
HIBP_HASH_RANGE_EMPTY = ""

# Various count levels for testing risk classification
HIBP_HASH_RANGE_LOW_COUNT = """1E4C9B93F3F0682250B6CF8331B7EE68FD8:5"""
HIBP_HASH_RANGE_MEDIUM_COUNT = """1E4C9B93F3F0682250B6CF8331B7EE68FD8:50"""
HIBP_HASH_RANGE_HIGH_COUNT = """1E4C9B93F3F0682250B6CF8331B7EE68FD8:500"""
HIBP_HASH_RANGE_CRITICAL_COUNT = """1E4C9B93F3F0682250B6CF8331B7EE68FD8:50000"""


# =============================================================================
# Breach API Mock Responses
# =============================================================================

HIBP_BREACH_RESPONSE = [
    {
        "Name": "Adobe",
        "Title": "Adobe",
        "Domain": "adobe.com",
        "BreachDate": "2013-10-04",
        "AddedDate": "2013-12-04T00:00:00Z",
        "ModifiedDate": "2022-05-15T23:52:49Z",
        "PwnCount": 152445165,
        "Description": "In October 2013, 153 million Adobe accounts were breached...",
        "LogoPath": "https://haveibeenpwned.com/Content/Images/PwnedLogos/Adobe.png",
        "DataClasses": [
            "Email addresses",
            "Password hints",
            "Passwords",
            "Usernames"
        ],
        "IsVerified": True,
        "IsFabricated": False,
        "IsSensitive": False,
        "IsRetired": False,
        "IsSpamList": False,
        "IsMalware": False,
        "IsSubscriptionFree": False,
        "IsStealerLog": False
    },
    {
        "Name": "LinkedIn",
        "Title": "LinkedIn",
        "Domain": "linkedin.com",
        "BreachDate": "2016-05-18",
        "AddedDate": "2016-05-21T00:00:00Z",
        "ModifiedDate": "2016-05-21T00:00:00Z",
        "PwnCount": 164611595,
        "Description": "In May 2016, LinkedIn had 164 million email addresses and passwords exposed...",
        "LogoPath": "https://haveibeenpwned.com/Content/Images/PwnedLogos/LinkedIn.png",
        "DataClasses": [
            "Email addresses",
            "Passwords"
        ],
        "IsVerified": True,
        "IsFabricated": False,
        "IsSensitive": False,
        "IsRetired": False,
        "IsSpamList": False,
        "IsMalware": False,
        "IsSubscriptionFree": False,
        "IsStealerLog": False
    },
    {
        "Name": "Collection1",
        "Title": "Collection #1",
        "Domain": "",
        "BreachDate": "2019-01-07",
        "AddedDate": "2019-01-16T00:00:00Z",
        "ModifiedDate": "2019-01-16T00:00:00Z",
        "PwnCount": 772904991,
        "Description": "In January 2019, a large collection of credential stuffing lists...",
        "LogoPath": "https://haveibeenpwned.com/Content/Images/PwnedLogos/List.png",
        "DataClasses": [
            "Email addresses",
            "Passwords"
        ],
        "IsVerified": False,
        "IsFabricated": False,
        "IsSensitive": False,
        "IsRetired": False,
        "IsSpamList": False,
        "IsMalware": False,
        "IsSubscriptionFree": False,
        "IsStealerLog": False
    },
    {
        "Name": "RedLineStealer",
        "Title": "RedLine Stealer Logs",
        "Domain": "",
        "BreachDate": "2023-06-15",
        "AddedDate": "2023-07-01T00:00:00Z",
        "ModifiedDate": "2023-07-01T00:00:00Z",
        "PwnCount": 5000000,
        "Description": "Credentials captured by RedLine stealer malware...",
        "LogoPath": "https://haveibeenpwned.com/Content/Images/PwnedLogos/List.png",
        "DataClasses": [
            "Email addresses",
            "Passwords",
            "Usernames",
            "Browser cookies"
        ],
        "IsVerified": True,
        "IsFabricated": False,
        "IsSensitive": False,
        "IsRetired": False,
        "IsSpamList": False,
        "IsMalware": True,
        "IsSubscriptionFree": False,
        "IsStealerLog": True
    },
    {
        "Name": "AdultFriendFinder",
        "Title": "Adult Friend Finder",
        "Domain": "adultfriendfinder.com",
        "BreachDate": "2016-10-01",
        "AddedDate": "2016-11-14T00:00:00Z",
        "ModifiedDate": "2016-11-14T00:00:00Z",
        "PwnCount": 412214295,
        "Description": "In October 2016, the adult entertainment company...",
        "LogoPath": "https://haveibeenpwned.com/Content/Images/PwnedLogos/AdultFriendFinder.png",
        "DataClasses": [
            "Email addresses",
            "Passwords",
            "Usernames"
        ],
        "IsVerified": True,
        "IsFabricated": False,
        "IsSensitive": True,
        "IsRetired": False,
        "IsSpamList": False,
        "IsMalware": False,
        "IsSubscriptionFree": False,
        "IsStealerLog": False
    }
]

# Response when email has no breaches (HTTP 404 from HIBP returns empty)
HIBP_BREACH_RESPONSE_EMPTY = []


# =============================================================================
# Paste API Mock Responses
# =============================================================================

HIBP_PASTE_RESPONSE = [
    {
        "Source": "Pastebin",
        "Id": "Ab8cDe9FgH",
        "Title": "Database dump 2023",
        "Date": "2023-03-15T14:30:00Z",
        "EmailCount": 15420
    },
    {
        "Source": "Ghostbin",
        "Id": "1234567890",
        "Title": None,
        "Date": "2022-11-20T08:15:00Z",
        "EmailCount": 5230
    },
    {
        "Source": "Pastebin",
        "Id": "XyZ987WvU",
        "Title": "leaked emails and passwords",
        "Date": "2021-06-10T22:45:00Z",
        "EmailCount": 89500
    }
]

# Empty paste response
HIBP_PASTE_RESPONSE_EMPTY = []


# =============================================================================
# Stealer Logs API Mock Responses
# =============================================================================

HIBP_STEALER_LOGS_RESPONSE = [
    "amazon.com",
    "paypal.com",
    "google.com",
    "facebook.com",
    "github.com",
    "bankofamerica.com",
    "chase.com",
    "netflix.com",
    "dropbox.com",
    "twitter.com"
]

# Empty stealer logs response
HIBP_STEALER_LOGS_RESPONSE_EMPTY = []


# =============================================================================
# Error Responses
# =============================================================================

HIBP_ERROR_401 = {
    "statusCode": 401,
    "message": "Access denied due to missing hibp-api-key."
}

HIBP_ERROR_403 = {
    "statusCode": 403,
    "message": "No user agent has been specified in the request."
}

HIBP_ERROR_429 = {
    "statusCode": 429,
    "message": "Rate limit exceeded."
}

HIBP_ERROR_503 = {
    "statusCode": 503,
    "message": "Service temporarily unavailable."
}


# =============================================================================
# Helper Functions
# =============================================================================

def get_hash_range_response(suffix: str, count: int) -> str:
    """Generate a hash range response containing a specific suffix and count.

    Args:
        suffix: The SHA1 hash suffix (35 characters, uppercase).
        count: The number of times the password appears in breaches.

    Returns:
        str: Formatted HIBP hash range response.
    """
    lines = [
        "0018A45C4D1DEF81644B54AB7F969B88D65:15",
        "003D68EB55068C33ACE09247EE4C639306B:3",
        f"{suffix}:{count}",
        "21BD10018A45C4D1DEF81644B54AB7F969B:4",
        "A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6E7:1",
    ]
    return "\n".join(lines)


def create_breach_response(
    name: str,
    title: str,
    breach_date: str,
    pwn_count: int,
    data_classes: list = None,
    is_stealer_log: bool = False,
    is_sensitive: bool = False,
    is_verified: bool = True,
    description: str = "",
) -> dict:
    """Create a custom breach response for testing.

    Args:
        name: The breach name identifier.
        title: Human-readable breach title.
        breach_date: Date of the breach (YYYY-MM-DD).
        pwn_count: Number of accounts affected.
        data_classes: List of compromised data types.
        is_stealer_log: Whether this is from stealer malware.
        is_sensitive: Whether this is a sensitive breach.
        is_verified: Whether the breach is verified.
        description: Breach description text.

    Returns:
        dict: A breach response object.
    """
    if data_classes is None:
        data_classes = ["Email addresses", "Passwords"]

    return {
        "Name": name,
        "Title": title,
        "Domain": f"{name.lower()}.com",
        "BreachDate": breach_date,
        "AddedDate": f"{breach_date}T00:00:00Z",
        "ModifiedDate": f"{breach_date}T00:00:00Z",
        "PwnCount": pwn_count,
        "Description": description or f"Breach of {title}",
        "LogoPath": f"https://haveibeenpwned.com/Content/Images/PwnedLogos/{name}.png",
        "DataClasses": data_classes,
        "IsVerified": is_verified,
        "IsFabricated": False,
        "IsSensitive": is_sensitive,
        "IsRetired": False,
        "IsSpamList": False,
        "IsMalware": is_stealer_log,
        "IsSubscriptionFree": False,
        "IsStealerLog": is_stealer_log,
    }
