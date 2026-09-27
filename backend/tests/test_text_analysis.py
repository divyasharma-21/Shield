"""Test cases for text and call transcript analysis."""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

client = TestClient(app)


def test_analyze_text_valid_suspicious():
    """Verify analysis of suspicious text returns all required contract fields."""
    payload = {
        "text": "Your electricity connection will be disconnected tonight at 9:30 PM. Call verification officer immediately.",
        "input_type": "sms"
    }
    response = client.post("/api/v1/analyze/text", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["module"] == "parent_call_guardian"
    assert data["status"] == "analyzed"
    assert data["predicted_label"] in ("suspicious", "legitimate")
    assert isinstance(data["suspicious_probability"], float)
    assert 0.0 <= data["suspicious_probability"] <= 1.0
    assert isinstance(data["selected_threshold"], float)
    assert data["safety_level"] in (
        "high_risk",
        "suspicious_needs_verification",
        "uncertain_needs_verification",
        "no_strong_risk_signal"
    )
    assert data["input_type"] == "sms"

    # Evidence contract
    assert "model_evidence" in data
    assert "signals_favoring_suspicious" in data["model_evidence"]
    assert "signals_favoring_legitimate" in data["model_evidence"]
    assert isinstance(data["model_evidence"]["signals_favoring_suspicious"], list)
    assert isinstance(data["model_evidence"]["signals_favoring_legitimate"], list)

    # Explanation contract
    assert "explanation" in data
    assert "summary" in data["explanation"]
    assert "evidence_summary" in data["explanation"]
    assert "uncertainty_note" in data["explanation"]

    # Recommended actions & disclaimer
    assert isinstance(data["recommended_actions"], list)
    assert len(data["recommended_actions"]) > 0
    assert "disclaimer" in data
    assert "text-based risk assessment" in data["disclaimer"]

    # Neutral wording check (no certainty claims)
    summary_lower = data["explanation"]["summary"].lower()
    assert "definitely a scammer" not in summary_lower
    assert "confirmed fraud" not in summary_lower
    assert "definitely safe" not in summary_lower


def test_analyze_call_transcript_valid():
    """Verify call transcript route enforces call_transcript input_type."""
    payload = {
        "text": "This is Inspector Sharma from Cyber Cell. You must transfer penalty funds immediately to avoid arrest.",
        "input_type": "call_transcript"
    }
    response = client.post("/api/v1/analyze/call/transcript", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["input_type"] == "call_transcript"
    assert data["safety_level"] in ("high_risk", "suspicious_needs_verification")
    assert data["suspicious_probability"] >= data["selected_threshold"]


def test_validation_error_on_short_input():
    """Input with fewer than 10 non-whitespace characters must return 422."""
    short_payloads = [
        {"text": "short", "input_type": "sms"},
        {"text": "   a b c   ", "input_type": "call_transcript"},
        {"text": "", "input_type": "whatsapp"}
    ]
    for p in short_payloads:
        response = client.post("/api/v1/analyze/text", json=p)
        assert response.status_code == 422, f"Failed for {p}"


def test_validation_error_on_invalid_input_type():
    """Unrecognized input_type must return 422."""
    payload = {
        "text": "Valid text with more than ten characters.",
        "input_type": "unrecognized_channel"
    }
    response = client.post("/api/v1/analyze/text", json=payload)
    assert response.status_code == 422
