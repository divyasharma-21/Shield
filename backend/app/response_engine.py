"""Response generator for SentryMesh Guardian.

Translates:
  - Detected category
  - Active psychological manipulation tactics
  - Extracted IOCs (UPI IDs, URLs, Phone numbers)
  - Verification signals

Into:
  - Concrete step-by-step human explanations (without technical jargon or criminal accusations)
  - Immediate defensive response actions (e.g. 1930 Cyber Fraud Helpline, UPI PIN warnings)
"""

from typing import Dict, List, Any


def generate_explanation(
    predicted_label: str,
    tactics: Dict[str, float],
    entities: Dict[str, Any],
    verification: Dict[str, Any],
    channel: str
) -> List[str]:
    """Builds evidence-based reasons explaining why the interaction was evaluated this way."""
    reasons = []

    # 1. Class-level explanation
    if predicted_label == "legitimate":
        reasons.append("The message structure and wording align with standard transactional notifications.")
        if entities.get("amounts"):
            reasons.append(f"Contains regular financial transaction or balance updates ({', '.join(entities['amounts'])}).")
        return reasons

    if predicted_label == "authority_impersonation_scam":
        reasons.append("The sender or caller claims to represent an enforcement agency, police, customs, or telecom authority demanding immediate compliance.")
    elif predicted_label == "UPI_QR_scam":
        reasons.append("The interaction requests you to approve a payment or enter your secret UPI PIN under the pretext of 'receiving' or 'claiming' money.")
    elif predicted_label == "remote_access_scam":
        reasons.append("The sender or caller instructs you to download remote support or screen-sharing software, which grants complete control over your phone or computer.")
    elif predicted_label == "fake_payment_scam":
        reasons.append("The message presents an unverified payment confirmation, escrow claim, or screenshot urging premature handover of goods or services.")
    elif predicted_label == "payment_or_credential_scam":
        reasons.append("The content solicits banking passwords, debit card numbers, CVVs, or OTP credentials to resolve an alleged account freeze.")
    elif predicted_label == "phishing":
        reasons.append("The communication directs you to an unverified external website attempting to capture your login credentials or personal data.")
    else:
        reasons.append("The interaction exhibits high-risk conversational patterns frequently observed in social engineering attempts.")

    # 2. Evidence from psychological manipulation tactics
    if tactics.get("urgency", 0) > 0.4:
        reasons.append("Extreme urgency detected: artificially short deadlines (e.g., 'within 2 hours', 'tonight at 9:30 PM') are used to provoke hasty decisions.")
    if tactics.get("fear_or_threat", 0) > 0.4:
        reasons.append("Intimidation tactics detected: mentions of arrest warrants, disconnection of utilities, or legal penalties designed to instill fear.")
    if tactics.get("secrecy", 0) > 0.4 or tactics.get("isolation", 0) > 0.4:
        reasons.append("Isolation pressure detected: instructing you to remain alone on a call or demanding confidentiality to prevent consulting family or officials.")
    if tactics.get("upi_collect_request", 0) > 0.4:
        reasons.append("UPI Reverse Trap: Prompts asking you to enter a UPI PIN to receive cashback or lottery funds. (In India UPI, entering a PIN always debits money).")
    if tactics.get("remote_access_request", 0) > 0.4 or tactics.get("screen_share_request", 0) > 0.4:
        reasons.append("Remote assistance prompt: Requesting you to install screen-sharing software or reveal session codes.")

    # 3. Evidence from verification signals
    if verification.get("is_known_threat_match"):
        reasons.append("Link verification: One or more embedded links match entries in verified threat intelligence feeds (PhishTank).")
    for df in verification.get("domain_findings", []):
        reasons.append(f"Domain analysis: {df}")

    return reasons


def generate_recommended_actions(
    predicted_label: str,
    tactics: Dict[str, float],
    entities: Dict[str, Any],
    verification: Dict[str, Any],
    channel: str
) -> List[str]:
    """Produces defensive countermeasures tailored to the specific vector."""
    actions = []

    if predicted_label == "legitimate":
        actions.append("No defensive action required for genuine transactional notifications.")
        actions.append("Reminder: Never share your OTP, bank PIN, or passwords with anyone, even if they claim to be bank representatives.")
        return actions

    # Universal immediate safety step
    actions.append("Do not click any embedded links, download files, or respond to the sender.")

    # Vector-specific actions
    if predicted_label == "UPI_QR_scam" or tactics.get("upi_collect_request", 0) > 0.3:
        actions.append("CRITICAL: Never enter your UPI PIN to receive money or cashback. UPI PIN is required ONLY when you are transferring money out.")
        actions.append("Decline any pending payment/collect requests inside your UPI app (Google Pay, PhonePe, Paytm, BHIM).")

    if predicted_label == "remote_access_scam" or tactics.get("remote_access_request", 0) > 0.3:
        actions.append("Do not install remote-desktop applications (AnyDesk, QuickSupport, TeamViewer) at the request of an unknown caller.")
        actions.append("If you have already installed software, immediately disconnect Wi-Fi / Mobile Data and uninstall the application.")

    if predicted_label == "authority_impersonation_scam" or tactics.get("fear_or_threat", 0) > 0.3:
        actions.append("Disconnect the call immediately. Indian police, CBI, customs, and telecom officials never place citizens under 'digital arrest' or demand money over video calls.")
        actions.append("Verify directly through official branch channels: contact your nearest police station or telecom service center independently.")

    if predicted_label == "fake_payment_scam":
        actions.append("Check your official bank statement or merchant soundbox directly before releasing any goods or services. Do not rely on buyer-provided screenshots or SMS.")

    if predicted_label == "payment_or_credential_scam" or tactics.get("credential_request", 0) > 0.3:
        actions.append("If you accidentally entered your password or card details, immediately block your debit/credit card via your official banking app or customer care.")

    # Helpline action
    actions.append("Report financial cyber fraud immediately to National Cyber Crime Helpline: Call 1930 or visit https://cybercrime.gov.in.")

    return actions
