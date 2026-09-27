"""Regex entity extractor and normalizer for SentryMesh Guardian.

Extracts Indicators of Compromise (IOCs):
- URLs and FQDN domains
- Email addresses
- Phone numbers (+91, Indian national, international formats)
- UPI IDs (*@okhdfcbank, *@paytm, *@invalid, etc.)
- Financial amounts (₹, INR, Rs., USD)

Privacy Redaction:
- Generates tokenized invariant text (<URL>, <EMAIL>, <PHONE>, <UPI_ID>, <MONEY>)
- Masks sensitive user identifiers in public or display contexts
"""

import re
import unicodedata
from typing import Any, Dict
from urllib.parse import urlparse


URL_PATTERN = (
    r"(?:https?:\/\/|www\.)[^\s<>\"]+|"
    r"[a-zA-Z0-9-]+\.(?:com|org|net|in|io|xyz|top|app|me|co|info|biz)"
    r"(?:\/[^\s<>\"]*)?"
)

EMAIL_PATTERN = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

UPI_PATTERN = (
    r"\b[a-zA-Z0-9_.-]+@(?:invalid|okhdfcbank|okaxis|okicici|paytm|"
    r"ybl|apl|upi|axl|ibl|barodampay|pnb|sbi)\b"
)

MONEY_PATTERN = (
    r"(?:Rs\.?|INR|₹|\$)\s*[\d,]+(?:\.\d+)?|"
    r"\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*(?:rupees|INR|USD)\b"
)

PHONE_PATTERN = (
    r"(?<!\d)"
    r"(?:\+91[\s-]*)?"
    r"[6-9]\d{4}[\s-]?\d{5}"
    r"(?!\d)"
    r"|\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    r"|\b0{5}[\s-]?0{5}\b"
)


def normalize_input_text(text: str) -> str:
    """Cleans Unicode characters, zero-width spaces, and superfluous whitespace."""
    if not isinstance(text, str):
        return ""

    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[\u200B-\u200D\uFEFF\u00AD]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def extract_entities(text: str) -> Dict[str, Any]:
    """Extracts IOCs from raw or normalized text."""
    clean = normalize_input_text(text)

    raw_urls = re.findall(URL_PATTERN, clean, flags=re.IGNORECASE)
    urls = list(dict.fromkeys(raw_urls))

    domains = []
    for url in urls:
        parsed = urlparse(url if "://" in url else f"http://{url}")
        host = parsed.netloc or parsed.path.split("/")[0]
        host = host.lower()

        if host.startswith("www."):
            host = host[4:]

        if host:
            domains.append(host)

    domains = list(dict.fromkeys(domains))

    raw_emails = re.findall(EMAIL_PATTERN, clean)
    emails = list(dict.fromkeys(raw_emails))

    raw_upis = re.findall(UPI_PATTERN, clean, flags=re.IGNORECASE)
    upi_ids = list(dict.fromkeys(raw_upis))

    emails = [
        email
        for email in emails
        if not any(email.lower() == upi.lower() for upi in upi_ids)
    ]

    raw_amounts = re.findall(MONEY_PATTERN, clean, flags=re.IGNORECASE)
    amounts = list(dict.fromkeys(raw_amounts))

    raw_phones = re.findall(PHONE_PATTERN, clean)
    phone_numbers = list(dict.fromkeys(raw_phones))

    return {
        "urls": urls,
        "domains": domains,
        "emails": emails,
        "phone_numbers": phone_numbers,
        "upi_ids": upi_ids,
        "amounts": amounts,
    }


def create_tokenized_text(text: str) -> str:
    """Replaces IOCs with standard representation tokens for semantic invariance."""
    s = normalize_input_text(text)

    # UPI must be replaced before generic email matching.
    s = re.sub(UPI_PATTERN, "<UPI_ID>", s, flags=re.IGNORECASE)

    # Email must be replaced before URL matching, otherwise the domain portion
    # of an email such as test@example.com can become test@<URL>.
    s = re.sub(EMAIL_PATTERN, "<EMAIL>", s)

    s = re.sub(URL_PATTERN, "<URL>", s, flags=re.IGNORECASE)
    s = re.sub(MONEY_PATTERN, "<MONEY>", s, flags=re.IGNORECASE)
    s = re.sub(PHONE_PATTERN, "<PHONE>", s)

    return re.sub(r"\s+", " ", s).strip()


def mask_pii(text: str) -> str:
    """Masks sensitive elements for public or community logging views."""
    s = normalize_input_text(text)

    def mask_phone_match(match):
        digits = re.sub(r"\D", "", match.group(0))

        if len(digits) >= 10:
            last3 = digits[-3:]
            return f"+91 XXXXX XX{last3}"

        return "+91 XXXXX XXXXX"

    s = re.sub(PHONE_PATTERN, mask_phone_match, s)

    # Email addresses are not needed for community threat intelligence and
    # should not survive into the quarantined sanitized representation.
    s = re.sub(EMAIL_PATTERN, lambda m: "[EMAIL_REDACTED]", s)

    # Mask likely account/card/reference number runs while preserving ordinary
    # URL paths and domains. This is intentionally conservative.
    def mask_account_number(match):
        value = match.group(0)
        digits = re.sub(r"\D", "", value)
        if 8 <= len(digits) <= 18:
            return "[ACCOUNT_NUMBER_REDACTED]"
        return value

    s = re.sub(r"(?<![A-Za-z0-9])(?:\d[ -]?){8,18}(?![A-Za-z0-9])", mask_account_number, s)

    def mask_upi_match(match):
        value = match.group(0)
        handle, provider = value.split("@", 1)

        if len(handle) > 1:
            return f"{handle[0]}***@{provider}"

        return f"***@{provider}"

    s = re.sub(UPI_PATTERN, mask_upi_match, s, flags=re.IGNORECASE)

    return s