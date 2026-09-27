import pytest

from app.analyzer import (
    calculate_entropy,
    evaluate_heuristic_classification,
    evaluate_heuristic_tactics,
    evaluate_tactics,
    analyze_communication,
)


def test_calculate_entropy_uniform_distribution():
    probabilities = {
        "legitimate": 0.5,
        "phishing": 0.5,
    }

    result = calculate_entropy(probabilities)

    assert result == pytest.approx(1.0)


def test_calculate_entropy_certain_distribution():
    probabilities = {
        "legitimate": 1.0,
        "phishing": 0.0,
    }

    result = calculate_entropy(probabilities)

    assert result == pytest.approx(0.0)


def test_evaluate_heuristic_classification_returns_valid_label():
    text = "Your monthly bank statement is now available."

    label, probabilities = evaluate_heuristic_classification(text, text)

    valid_labels = {
        "legitimate",
        "phishing",
        "payment_or_credential_scam",
        "authority_impersonation_scam",
        "remote_access_scam",
        "UPI_QR_scam",
        "fake_payment_scam",
        "other_suspicious",
    }

    assert label in valid_labels
    assert isinstance(probabilities, dict)
    assert abs(sum(probabilities.values()) - 1.0) < 0.01


def test_heuristic_detects_remote_access_scam():
    text = "Install AnyDesk and share the remote access code."

    label, probabilities = evaluate_heuristic_classification(text, text)

    assert label == "remote_access_scam"
    assert probabilities["remote_access_scam"] > 0.5


def test_heuristic_detects_authority_impersonation():
    text = "This is a CBI officer. There is an arrest warrant against you."

    label, probabilities = evaluate_heuristic_classification(text, text)

    assert label == "authority_impersonation_scam"
    assert probabilities["authority_impersonation_scam"] > 0.5


def test_heuristic_detects_upi_scam():
    text = "To receive cashback, enter your 6-digit UPI PIN."

    label, probabilities = evaluate_heuristic_classification(text, text)

    assert label == "UPI_QR_scam"
    assert probabilities["UPI_QR_scam"] > 0.5


def test_heuristic_detects_fake_payment():
    text = "Payment successful! Rs 500 has been transferred."

    label, probabilities = evaluate_heuristic_classification(text, text)

    assert label == "fake_payment_scam"
    assert probabilities["fake_payment_scam"] > 0.5


def test_heuristic_detects_phishing():
    text = "Your KYC update is required. Click the link to reactivate-card."

    label, probabilities = evaluate_heuristic_classification(text, text)

    assert label in {
        "phishing",
        "payment_or_credential_scam",
    }


def test_heuristic_detects_legitimate_otp_message():
    text = "Your OTP is 123456. Never share this OTP with anyone."

    label, probabilities = evaluate_heuristic_classification(text, text)

    assert label == "legitimate"


def test_heuristic_detects_legitimate_salary_message():
    text = "Salary credited by employer. Available balance is Rs 50000."

    label, probabilities = evaluate_heuristic_classification(text, text)

    assert label == "legitimate"


def test_heuristic_detects_legitimate_statement():
    text = "Your monthly statement is available for download."

    label, probabilities = evaluate_heuristic_classification(text, text)

    assert label == "legitimate"


# ---------------------------------------------------------------------------
# Heuristic tactic detector tests
# ---------------------------------------------------------------------------

def test_heuristic_tactics_detects_authority():
    text = "I am a bank officer calling from the cyber office."

    tactics = evaluate_heuristic_tactics(text)

    assert tactics["authority_impersonation"] == 0.92


def test_heuristic_tactics_detects_urgency():
    text = "Act immediately. Your account will expire today."

    tactics = evaluate_heuristic_tactics(text)

    assert tactics["urgency"] == 0.88


def test_heuristic_tactics_detects_multiple_scam_tactics():
    text = (
        "I am a bank officer. Block your account immediately. "
        "Tell me OTP and transfer the penalty."
    )

    tactics = evaluate_heuristic_tactics(text)

    assert tactics["authority_impersonation"] == 0.92
    assert tactics["urgency"] == 0.88
    assert tactics["fear_or_threat"] == 0.90
    assert tactics["otp_request"] == 0.89
    assert tactics["payment_request"] == 0.82


def test_heuristic_tactics_detects_secrecy():
    text = "Do not tell anyone about this confidential matter."

    tactics = evaluate_heuristic_tactics(text)

    assert tactics["secrecy"] == 0.85


def test_heuristic_tactics_detects_isolation():
    text = "Stay on video call and do not disconnect."

    tactics = evaluate_heuristic_tactics(text)

    assert tactics["isolation"] == 0.95


def test_heuristic_tactics_detects_credentials():
    text = "Please provide your password and CVV."

    tactics = evaluate_heuristic_tactics(text)

    assert tactics["credential_request"] == 0.87


def test_heuristic_tactics_detects_remote_access():
    text = "Install AnyDesk and connect to support."

    tactics = evaluate_heuristic_tactics(text)

    assert tactics["remote_access_request"] == 0.96


def test_heuristic_tactics_detects_screen_share():
    text = "Share your screen and read out the code."

    tactics = evaluate_heuristic_tactics(text)

    assert tactics["screen_share_request"] == 0.94


def test_heuristic_tactics_detects_upi_collect():
    text = "Accept this UPI collect request."

    tactics = evaluate_heuristic_tactics(text)

    assert tactics["upi_collect_request"] == 0.95


# ---------------------------------------------------------------------------
# Trained ML tactic model tests
# ---------------------------------------------------------------------------

def test_trained_tactics_returns_all_tactics():
    from app.model_loader import get_model_manager

    model_mgr = get_model_manager()
    model_mgr.load_models_if_needed()

    text = "URGENT! Your bank account will be blocked. Contact the officer now."

    tactics = evaluate_tactics(
        text,
        text,
        model_mgr,
    )

    expected_tactics = {
        "authority_impersonation",
        "urgency",
        "fear_or_threat",
        "secrecy",
        "isolation",
        "payment_request",
        "otp_request",
        "credential_request",
        "remote_access_request",
        "screen_share_request",
        "upi_collect_request",
    }

    assert set(tactics.keys()) == expected_tactics


def test_trained_tactics_return_probability_range():
    from app.model_loader import get_model_manager

    model_mgr = get_model_manager()
    model_mgr.load_models_if_needed()

    text = "URGENT! Your account will be blocked immediately."

    tactics = evaluate_tactics(
        text,
        text,
        model_mgr,
    )

    assert all(
        0.0 <= value <= 1.0
        for value in tactics.values()
    )


def test_trained_tactics_detect_strong_authority_and_urgency():
    from app.model_loader import get_model_manager

    model_mgr = get_model_manager()
    model_mgr.load_models_if_needed()

    text = (
        "URGENT! Your bank account will be blocked today. "
        "Call the officer immediately."
    )

    tactics = evaluate_tactics(
        text,
        text,
        model_mgr,
    )

    assert tactics["authority_impersonation"] > 0.5
    assert tactics["urgency"] > 0.5


def test_tactics_fallback_without_model():
    class EmptyModelManager:
        tactic_model = None
        embedder = None

    text = "Act immediately. Your account will expire today."

    tactics = evaluate_tactics(
        text,
        text,
        EmptyModelManager(),
    )

    assert tactics["urgency"] == 0.88


# ---------------------------------------------------------------------------
# Full analyzer tests
# ---------------------------------------------------------------------------

def test_analyze_communication_returns_expected_structure():
    text = "Your monthly statement is available."

    result = analyze_communication(text)

    assert isinstance(result, dict)

    assert "classification" in result
    assert "entities" in result
    assert "tactics" in result
    assert "verification" in result
    assert "explanation" in result
    assert "recommended_actions" in result
    assert "uncertainty" in result


def test_analyze_communication_has_classification_fields():
    text = "Your monthly statement is available."

    result = analyze_communication(text)

    classification = result["classification"]

    assert "predicted_label" in classification
    assert "probabilities" in classification
    assert isinstance(classification["probabilities"], dict)


def test_analyze_communication_detects_tactics():
    text = (
        "URGENT! Block your account immediately. "
        "Transfer Rs. 500 now."
    )

    result = analyze_communication(text)

    tactics = result["tactics"]

    assert 0.0 <= tactics["urgency"] <= 1.0
    assert 0.0 <= tactics["fear_or_threat"] <= 1.0
    assert 0.0 <= tactics["payment_request"] <= 1.0

    assert tactics["urgency"] > 0.5


def test_analyze_communication_passes_channel_to_response_layer(monkeypatch):
    captured = {}

    def fake_explanation(**kwargs):
        captured["explanation_channel"] = kwargs.get("channel")
        return "test explanation"

    def fake_actions(**kwargs):
        captured["actions_channel"] = kwargs.get("channel")
        return ["Do not respond"]

    monkeypatch.setattr(
        "app.analyzer.generate_explanation",
        fake_explanation,
    )

    monkeypatch.setattr(
        "app.analyzer.generate_recommended_actions",
        fake_actions,
    )

    result = analyze_communication(
        "Your account will be blocked immediately.",
        channel="whatsapp",
    )

    assert result["explanation"] == "test explanation"
    assert result["recommended_actions"] == ["Do not respond"]
    assert captured["explanation_channel"] == "whatsapp"
    assert captured["actions_channel"] == "whatsapp"


def test_analyze_communication_handles_empty_text():
    result = analyze_communication("")

    assert isinstance(result, dict)
    assert "classification" in result
    assert "uncertainty" in result


def test_analyzer_does_not_make_criminal_accusation():
    result = analyze_communication(
        "Block your account immediately."
    )

    combined = (
        str(result["explanation"])
        + " "
        + str(result["recommended_actions"])
    ).lower()

    assert "criminal" not in combined
    assert "criminal activity" not in combined


def test_uncertainty_is_valid_label():
    result = analyze_communication(
        "This is a routine notification."
    )

    assert result["uncertainty"] in {
        "low",
        "medium",
        "high",
    }