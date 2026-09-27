"""Test cases for GET /api/v1/health."""

import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify health endpoint returns ok, model loaded status, and dynamic threshold."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["model_loaded"] is True
    assert data["model_name"] == "sentrymesh_binary_tfidf_v4"
    assert isinstance(data["selected_suspicious_threshold"], float)
    assert data["selected_suspicious_threshold"] > 0.0
    assert data["audio_transcription_configured"] is False
    assert data["voice_authenticity_configured"] is False
