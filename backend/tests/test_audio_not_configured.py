"""Test cases for audio upload when transcription is not configured."""

import sys
import io
from pathlib import Path
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

client = TestClient(app)


def test_audio_not_configured_returns_501():
    """When ENABLE_AUDIO_TRANSCRIPTION is false, uploading audio must return 501."""
    fake_audio_bytes = b"RIFF....WAVEfmt ...."
    files = {
        "file": ("test_recording.wav", io.BytesIO(fake_audio_bytes), "audio/wav")
    }

    response = client.post("/api/v1/analyze/call/audio", files=files)
    assert response.status_code == 501
    data = response.json()

    assert "detail" in data
    detail = data["detail"]
    assert detail["module"] == "parent_call_audio"
    assert detail["status"] == "not_configured"
    assert "No transcript-risk result has been generated" in detail["message"]


def test_unsupported_audio_extension_returns_400():
    """Uploading non-audio files (e.g. .txt, .exe) must return 400."""
    fake_file = io.BytesIO(b"malicious or invalid content")
    files = {
        "file": ("suspicious.exe", fake_file, "application/octet-stream")
    }

    response = client.post("/api/v1/analyze/call/audio", files=files)
    assert response.status_code == 400
    assert "Unsupported audio format" in response.text
