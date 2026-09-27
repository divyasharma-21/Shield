
"""Tests for SentryMesh entity extraction and privacy-safe normalization."""

import pytest

from app.extractor import (
    create_tokenized_text,
    extract_entities,
    mask_pii,
    normalize_input_text,
)


def test_normalize_input_text():
    text = "  Hello\u200b   world \n\t from SentryMesh  "

    result = normalize_input_text(text)

    assert result == "Hello world from SentryMesh"


def test_normalize_non_string_input():
    assert normalize_input_text(None) == ""
    assert normalize_input_text(12345) == ""


def test_extract_url_and_domain():
    text = (
        "Please visit https://example.com/login and "
        "also check www.example.org/verify."
    )

    result = extract_entities(text)

    assert "https://example.com/login" in result["urls"]
    assert "www.example.org/verify." in result["urls"]

    assert "example.com" in result["domains"]
    assert "example.org" in result["domains"]


def test_extract_email():
    text = "Contact security@example.com or support@company.in."

    result = extract_entities(text)

    assert "security@example.com" in result["emails"]
    assert "support@company.in" in result["emails"]


def test_extract_indian_phone_number():
    text = "Call +91 98765 43210 or 9123456789 immediately."

    result = extract_entities(text)

    assert "+91 98765 43210" in result["phone_numbers"]
    assert "9123456789" in result["phone_numbers"]


def test_extract_upi_id():
    text = "Pay ₹500 to demo.user@paytm immediately."

    result = extract_entities(text)

    assert "demo.user@paytm" in result["upi_ids"]


def test_upi_id_is_not_returned_as_email():
    text = "Send payment to demo.user@paytm."

    result = extract_entities(text)

    assert "demo.user@paytm" in result["upi_ids"]
    assert "demo.user@paytm" not in result["emails"]


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Pay Rs. 500 now", "Rs. 500"),
        ("Transfer INR 1,250", "INR 1,250"),
        ("You won ₹50,000", "₹50,000"),
        ("Pay $25", "$25"),
        ("Send 500 rupees", "500 rupees"),
    ],
)
def test_extract_amounts(text, expected):
    result = extract_entities(text)

    assert expected in result["amounts"]


def test_entity_deduplication():
    text = (
        "Visit https://example.com and https://example.com "
        "or email test@example.com test@example.com."
    )

    result = extract_entities(text)

    assert result["urls"].count("https://example.com") == 1
    assert result["emails"].count("test@example.com") == 1


def test_empty_text_returns_empty_entities():
    result = extract_entities("")

    assert result == {
        "urls": [],
        "domains": [],
        "emails": [],
        "phone_numbers": [],
        "upi_ids": [],
        "amounts": [],
    }


def test_create_tokenized_text():
    text = (
        "Visit https://example.com/login, "
        "email test@example.com, "
        "call +91 98765 43210, "
        "or pay ₹500 to demo@paytm."
    )

    result = create_tokenized_text(text)

    assert "<URL>" in result
    assert "<EMAIL>" in result
    assert "<PHONE>" in result
    assert "<MONEY>" in result
    assert "<UPI_ID>" in result

    assert "example.com" not in result
    assert "test@example.com" not in result
    assert "98765" not in result


def test_create_tokenized_text_preserves_semantic_text():
    text = "Your account requires immediate verification."

    result = create_tokenized_text(text)

    assert result == text


def test_mask_pii_phone():
    text = "Call +91 98765 43210 for assistance."

    result = mask_pii(text)

    assert "98765 43210" not in result
    assert "+91 XXXXX XX210" in result


def test_mask_pii_upi():
    text = "Payment sent to rahul.sharma@paytm."

    result = mask_pii(text)

    assert "rahul.sharma@paytm" not in result
    assert "r***@paytm" in result


def test_mask_pii_does_not_remove_normal_text():
    text = "Please verify your account before continuing."

    result = mask_pii(text)

    assert result == text


def test_extraction_does_not_classify_message():
    """Extractor should return entities only, never a fraud classification."""

    text = (
        "URGENT! Your account is blocked. "
        "Visit https://example.com and pay ₹500."
    )

    result = extract_entities(text)

    assert "urls" in result
    assert "amounts" in result

    # Classification must happen in the trained model/analyzer layer,
    # not in the entity extractor.
    assert "label" not in result
    assert "prediction" not in result
    assert "risk" not in result
    assert "fraud" not in result
