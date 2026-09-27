"""Privacy-preserving ReportGuard intake and quarantine.

Raw submissions are never persisted by this service. A sanitized representation
is written to an isolated quarantine directory for later authorized review.
No submission is automatically promoted to a training dataset.
"""

import datetime
import json
import re
import uuid
from pathlib import Path
from typing import Any, Dict

from app.extractor import mask_pii, extract_entities

BASE_DIR = Path(__file__).resolve().parents[1]
QUARANTINE_DIR = BASE_DIR / "data" / "user_reports" / "quarantine"


def _sanitize(value: str | None) -> str:
    return mask_pii(value or "").strip()


def submit_user_report(data: dict) -> dict:
    """Sanitize, quarantine and return a review receipt.

    The persisted record intentionally contains only sanitized text and
    metadata. The original submission is not stored in the quarantine file.
    """
    raw_text = str(data.get("text") or "").strip()
    raw_notes = str(data.get("user_notes") or "").strip()

    if not raw_text:
        raise ValueError("Report content cannot be empty.")

    sanitized_text = _sanitize(raw_text)
    sanitized_notes = _sanitize(raw_notes) if raw_notes else None

    original_entities = extract_entities(raw_text)
    masked_entities = extract_entities(sanitized_text)

    explicit_urls = re.findall(
        r"https?://[^\s<>]+",
        raw_text,
        flags=re.IGNORECASE,
    )

    pii_counts = {
        "emails": len(original_entities.get("emails", [])),
        "phone_numbers": len(original_entities.get("phone_numbers", [])),
        "upi_ids": len(original_entities.get("upi_ids", [])),
    }

    observed_evidence = []

    if pii_counts["emails"]:
        observed_evidence.append({
            "signal": "Email identifier",
            "reason": (
                f'{pii_counts["emails"]} email identifier(s) detected '
                "and redacted before quarantine."
            ),
        })

    if pii_counts["phone_numbers"]:
        observed_evidence.append({
            "signal": "Phone identifier",
            "reason": (
                f'{pii_counts["phone_numbers"]} phone number(s) detected '
                "and redacted before quarantine."
            ),
        })

    if pii_counts["upi_ids"]:
        observed_evidence.append({
            "signal": "UPI identifier",
            "reason": (
                f'{pii_counts["upi_ids"]} UPI identifier(s) detected '
                "and redacted before quarantine."
            ),
        })

    if explicit_urls:
        observed_evidence.append({
            "signal": "Security URL preserved",
            "reason": (
                f"{len(explicit_urls)} URL(s) were preserved as "
                "investigation evidence rather than redacted."
            ),
        })

    if re.search(
        r"\b(?:otp|one[- ]time password|verification code|security code)\b",
        raw_text,
        re.I,
    ):
        observed_evidence.append({
            "signal": "Credential-code request",
            "reason": (
                "The report contains OTP/verification-code language "
                "that may be relevant to a security review."
            ),
        })

    if re.search(
        r"\b(?:password|passcode|pin|upi pin|cvv|login|sign in|verify your account)\b",
        raw_text,
        re.I,
    ):
        observed_evidence.append({
            "signal": "Credential/account language",
            "reason": (
                "The report contains account or credential-related language."
            ),
        })

    if re.search(
        r"\b(?:urgent|immediately|act now|expires today|blocked today)\b",
        raw_text,
        re.I,
    ):
        observed_evidence.append({
            "signal": "Urgency language",
            "reason": (
                "The report contains urgency language that can be relevant "
                "when reviewing social-engineering attempts."
            ),
        })

    report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    record: Dict[str, Any] = {
        "report_id": report_id,
        "timestamp": timestamp,
        "status": "pending_moderator_review",
        "channel": data.get("channel", "sms"),
        "suspected_label": data.get("suspected_label"),
        "sanitized_text": sanitized_text,
        "sanitized_reviewer_note": sanitized_notes,
        "sanitization": {
            "applied": True,
            "pii_detected": any(pii_counts.values()),
            "redacted_counts": pii_counts,
            "security_entities_preserved": {
                "urls": explicit_urls,
                "domains": sorted({
                    u.split("/", 3)[2]
                    .split("@")[-1]
                    .split(":")[0]
                    .lower()
                    for u in explicit_urls
                }),
                "amounts": masked_entities.get("amounts", []),
            },
            "observed_evidence": observed_evidence,
        },
        "consent_anonymized_research": bool(
            data.get("consent_anonymized_research", False)
        ),
        "training_ingestion": "blocked_pending_human_review",
        "retention_note": (
            "Only the sanitized quarantine representation is "
            "persisted by this service."
        ),
    }

    report_file = QUARANTINE_DIR / f"{report_id}.json"

    report_file.write_text(
        json.dumps(record, indent=2),
        encoding="utf-8",
    )

    return {
        "report_id": report_id,
        "timestamp": timestamp,
        "status": record["status"],
        "channel": record["channel"],
        "sanitized_text": sanitized_text,
        "sanitized_reviewer_note": sanitized_notes,
        "sanitization": record["sanitization"],
        "training_ingestion": record["training_ingestion"],
        "retention_note": record["retention_note"],
        "message": (
            "Report sanitized and placed in the moderator quarantine. "
            "It is not automatically added to training data."
        ),
    }


def get_quarantine_report(report_id: str) -> dict | None:
    path = QUARANTINE_DIR / f"{report_id}.json"

    if not path.exists():
        return None

    return json.loads(
        path.read_text(encoding="utf-8")
    )