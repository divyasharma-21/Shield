"""Test cases for family share summary endpoint."""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

client = TestClient(app)


def test_family_share_summary_generation():
    """Verify family summary is generated strictly from provided model results."""
    payload = {
        "safety_level": "suspicious_needs_verification",
        "suspicious_probability": 0.654,
        "evidence_summary": [
            "Model-influential phrasing included 'electricity connection', 'cut tonight'."
        ],
        "recommended_actions": [
            "Pause before acting. Do not send money or approve collect requests.",
            "Verify with electricity provider directly."
        ],
        "disclaimer": "This is a text-based risk assessment."
    }

    response = client.post("/api/v1/family/share-summary", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "SentryMesh Guardian Alert"
    assert data["safety_level"] == "suspicious_needs_verification"
    assert "Suspicious" in data["safety_level_display"]
    assert "electricity connection" in data["why_text"]
    assert "Pause before acting" in data["recommended_action_text"]
    assert "text-based risk assessment" in data["disclaimer_text"]
    assert "🛡️ SentryMesh Guardian Family Alert" in data["full_share_text"]
    assert "Pause. Verify. Protect." in data["full_share_text"]
