import io
import sys
from pathlib import Path

from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

client = TestClient(app)


def test_report_requires_explicit_consent():
    response = client.post('/report', json={
        'text': 'Suspicious link https://example.com/login',
        'channel': 'sms',
        'user_consent': False,
    })
    assert response.status_code == 400


def test_report_quarantine_redacts_pii_and_preserves_url():
    response = client.post('/report', json={
        'text': 'Email rahul.mehta@gmail.com Phone +91 9876543210 Account 123456789012 Visit https://sbi-login-security.xyz/verify-account',
        'channel': 'sms',
        'user_consent': True,
    })
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'pending_moderator_review'
    assert data['sanitization']['pii_detected'] is True
    assert 'https://sbi-login-security.xyz/verify-account' in data['sanitization']['security_entities_preserved']['urls']


def test_unknown_app_is_unverified_not_zero_percent():
    response = client.post('/appguard', json={
        'app_name': 'DefinitelyNotARealApp123',
        'installation_source': 'Unknown / not provided',
        'user_consent': True,
    })
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'unverified'
    assert data['risk_score'] is None
    assert data['risk_level'] == 'unverified'


def test_known_app_has_explainable_evidence():
    response = client.post('/appguard', json={
        'app_name': 'WhatsApp',
        'installation_source': 'Google Play',
        'user_consent': True,
    })
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'analyzed'
    assert data['explainable_report']['evidence_items']


def test_webguard_returns_score_evidence_items():
    response = client.post('/webguard', json={
        'url': 'https://sbi-login-security.xyz/verify-account',
        'resolve_dns': False,
        'user_consent': True,
    })
    assert response.status_code == 200
    data = response.json()
    items = data['explainable_report']['evidence_items']
    assert items
    assert any(item['label'] == 'Possible brand impersonation' for item in items)
    assert all('reason' in item for item in items)
