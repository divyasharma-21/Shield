"""Unit and integration tests for SentryMesh Guardian core pipeline."""

import pytest
from app.extractor import extract_entities, create_tokenized_text, mask_pii
from app.verifier import get_verifier
from app.analyzer import analyze_communication


def test_ioc_extraction():
    sample_text = (
        "Transfer Rs 15,000 to demo_refund@invalid using link "
        "http://invalid.example/verify or call +91 00000 00000."
    )
    entities = extract_entities(sample_text)

    assert "demo_refund@invalid" in entities["upi_ids"]
    assert any("invalid.example" in u for u in entities["urls"])
    assert len(entities["amounts"]) >= 1
    assert len(entities["phone_numbers"]) >= 1


def test_tokenized_text():
    sample_text = "Call +91 00000 00000 and send Rs 500 to demo_payment@invalid"
    tokenized = create_tokenized_text(sample_text)

    assert "<PHONE>" in tokenized
    assert "<MONEY>" in tokenized
    assert "<UPI_ID>" in tokenized


def test_pii_masking():
    sample = "User phone is +91 98765 43210 and upi is rahul.sharma@paytm"
    masked = mask_pii(sample)

    assert "98765" not in masked
    assert "XX" in masked
    assert "rahul.sharma" not in masked


def test_legitimate_otp_not_shortcut_flagged():
    # Legitimate bank OTP alert should NOT be labeled as scam
    legit_msg = (
        "123456 is your secret OTP for login to Example Bank NetBanking. "
        "Never share your OTP with anyone including bank staff. OTP valid for 5 mins."
    )
    res = analyze_communication(legit_msg, channel="sms")

    assert res["classification"]["predicted_label"] == "legitimate"
    assert "Never share your OTP" in " ".join(res["recommended_actions"])


def test_digital_arrest_call_detection():
    scam_call = (
        "This is Inspector Rao from Central Crime Branch. You are under immediate "
        "digital arrest for money laundering. Stay on video call and do not disconnect."
    )
    res = analyze_communication(scam_call, channel="call")

    assert res["classification"]["predicted_label"] == "authority_impersonation_scam"
    assert res["tactics"]["authority_impersonation"] > 0.5
    assert res["tactics"]["isolation"] > 0.5
    assert any("1930" in act for act in res["recommended_actions"])


def test_upi_qr_reverse_scam_detection():
    upi_scam = (
        "Congratulations! You won Rs 25,000 cash prize. Enter your secret "
        "6-digit UPI PIN to receive money into your bank account immediately."
    )
    res = analyze_communication(upi_scam, channel="qr")

    assert res["classification"]["predicted_label"] == "UPI_QR_scam"
    assert res["tactics"]["upi_collect_request"] > 0.5
    assert any("Never enter your UPI PIN to receive money" in act for act in res["recommended_actions"])
