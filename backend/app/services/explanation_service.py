"""Explanation and recommended actions service for SentryMesh Guardian.

Constructs neutral, plain-language explanations and safety actions
strictly derived from actual model probabilities, threshold, safety level,
and attribution features.
Never claims certainty and uses no keyword-only decision rules.
"""

from typing import List, Tuple
from app.schemas import (
    SafetyLevel,
    InputType,
    ModelEvidence,
    ExplanationBlock
)

INPUT_TYPE_LABELS = {
    "call_transcript": "call transcript",
    "sms": "SMS message",
    "whatsapp": "WhatsApp message",
    "email": "email",
    "payment_message": "payment communication",
    "social_message": "social media message"
}


def build_explanation(
    safety_level: SafetyLevel,
    suspicious_probability: float,
    selected_threshold: float,
    evidence: ModelEvidence,
    input_type: InputType
) -> Tuple[ExplanationBlock, List[str]]:
    """Builds an evidence-based, non-alarmist explanation and safety action checklist."""

    type_label = INPUT_TYPE_LABELS.get(input_type, "submitted communication")
    pct_prob = f"{suspicious_probability * 100:.1f}%"
    pct_thresh = f"{selected_threshold * 100:.1f}%"

    # 1. Summary statement strictly reflecting safety level
    if safety_level == "high_risk":
        summary = (
            f"The model calculated a {pct_prob} suspicious probability (well above the {pct_thresh} threshold). "
            f"The language in this {type_label} strongly aligned with patterns seen in known scam and coercion attempts."
        )
    elif safety_level == "suspicious_needs_verification":
        summary = (
            f"The model found language that contributed toward a suspicious-risk assessment "
            f"({pct_prob} probability, reaching the {pct_thresh} verification threshold). "
            f"The system recommends pausing before responding."
        )
    elif safety_level == "uncertain_needs_verification":
        summary = (
            f"The model's assessment of this {type_label} is in the uncertain range "
            f"({pct_prob} probability, close to the {pct_thresh} threshold). "
            f"Because text signals are ambiguous, treat requests for funds, credentials, or access with heightened caution."
        )
    else:  # no_strong_risk_signal
        summary = (
            f"No strong scam signal was detected in this {type_label} "
            f"({pct_prob} probability, below the {pct_thresh} threshold). "
            f"However, this is not a guarantee that the sender or caller is legitimate."
        )

    # 2. Evidence summary phrases from real attribution
    evidence_summary: List[str] = []

    if evidence.signals_favoring_suspicious:
        susp_features = [f"'{item.feature}'" for item in evidence.signals_favoring_suspicious[:3]]
        evidence_summary.append(
            f"Model-influential phrasing contributing toward suspicion included: {', '.join(susp_features)}."
        )

    if evidence.signals_favoring_legitimate:
        legit_features = [f"'{item.feature}'" for item in evidence.signals_favoring_legitimate[:3]]
        evidence_summary.append(
            f"Phrasing that weighted toward a standard or legitimate pattern included: {', '.join(legit_features)}."
        )

    if not evidence_summary:
        evidence_summary.append(
            "The model evaluated the general sentence composition without single dominant vocabulary spikes."
        )

    uncertainty_note = (
        "This is a text-based risk assessment and does not prove that a caller or message is fraudulent. "
        "The system cannot verify caller identity solely from submitted text."
    )

    explanation_block = ExplanationBlock(
        summary=summary,
        evidence_summary=evidence_summary,
        uncertainty_note=uncertainty_note
    )

    # 3. Recommended Actions strictly tailored to safety level and vector
    recommended_actions: List[str] = []

    if safety_level == "high_risk":
        recommended_actions.append(
            "Pause immediately. Do not send money, approve UPI collect requests, or enter your UPI PIN."
        )
        recommended_actions.append(
            "Never share OTPs, passwords, card numbers, or NetBanking credentials under any circumstance."
        )
        recommended_actions.append(
            "Do not install remote-support tools (such as AnyDesk, TeamViewer, or QuickSupport) or share your screen."
        )
        if input_type in ("call_transcript",):
            recommended_actions.append(
                "Disconnect the call. Official law enforcement or government agencies do not arrest people over video calls or demand money to clear cases."
            )
        recommended_actions.append(
            "Verify independently using an official app, bank branch, or verified website."
        )
    elif safety_level == "suspicious_needs_verification":
        recommended_actions.append(
            "Pause before acting. Do not approve unexpected payment or collect requests."
        )
        recommended_actions.append(
            "Do not share verification codes, passwords, or personal credentials."
        )
        recommended_actions.append(
            "Verify the caller or sender's identity independently using a published official contact."
        )
        if input_type in ("payment_message", "sms", "whatsapp"):
            recommended_actions.append(
                "Remember: Entering a UPI PIN always deducts money from your account; you never enter a PIN to receive a refund or prize."
            )
    elif safety_level == "uncertain_needs_verification":
        recommended_actions.append(
            "Treat any request for money, OTPs, UPI PINs, or device access as high risk until independently verified."
        )
        recommended_actions.append(
            "Call the family member, bank, or organization directly on a trusted, independently saved phone number."
        )
        recommended_actions.append(
            "Never click unfamiliar links or scan payment QR codes sent in unverified messages."
        )
    else:  # no_strong_risk_signal
        recommended_actions.append(
            "No strong text risk was found, but continue exercising standard caution."
        )
        recommended_actions.append(
            "Never share OTPs, passwords, or remote screen access with any unverified caller or contact."
        )
        recommended_actions.append(
            "If the message asks for unexpected financial action, verify through an official channel first."
        )

    return explanation_block, recommended_actions
