"""Family Circle summary generation service for SentryMesh Guardian.

Formats a safe, clear summary suitable for family verification.
Strictly relies on actual model assessment data without inventing facts.
"""

from typing import List
from app.schemas import (
    FamilyShareRequest,
    FamilyShareResponse,
    SafetyLevel
)

SAFETY_LEVEL_DISPLAY = {
    "high_risk": "High Risk — Immediate Action Needed",
    "suspicious_needs_verification": "Suspicious — Needs Verification",
    "uncertain_needs_verification": "Uncertain — Verification Required",
    "no_strong_risk_signal": "No Strong Risk Signal Found"
}


def create_family_share_summary(payload: FamilyShareRequest) -> FamilyShareResponse:
    """Creates a concise, parent-friendly summary from completed analysis results."""
    display_level = SAFETY_LEVEL_DISPLAY.get(
        payload.safety_level,
        payload.safety_level.replace("_", " ").title()
    )

    # Why text derived from actual evidence summary
    if payload.evidence_summary:
        why_text = " ".join(payload.evidence_summary)
    else:
        why_text = f"The model evaluated text features and calculated a {payload.suspicious_probability * 100:.1f}% risk score."

    # Recommended action derived from actions
    if payload.recommended_actions:
        action_text = " ".join(payload.recommended_actions[:2])
    else:
        action_text = (
            "Please pause before taking any action. Do not send money, share OTPs, "
            "install remote apps, or provide passwords until independently verified."
        )

    disclaimer_text = (
        payload.disclaimer
        or "This is a text-based risk assessment, not proof that a caller or message is fraudulent."
    )

    # Formatted plain-text block for clipboard / messenger sharing
    full_share_text = (
        f"🛡️ SentryMesh Guardian Family Alert\n\n"
        f"Risk Level: {display_level}\n\n"
        f"Why:\n{why_text}\n\n"
        f"Recommended Action:\n{action_text}\n\n"
        f"Note: {disclaimer_text}\n"
        f"Verification Rule: Pause. Verify. Protect."
    )

    return FamilyShareResponse(
        title="SentryMesh Guardian Alert",
        safety_level=payload.safety_level,
        safety_level_display=display_level,
        why_text=why_text,
        recommended_action_text=action_text,
        disclaimer_text=disclaimer_text,
        full_share_text=full_share_text
    )
