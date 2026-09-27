"""Central orchestrator for SentryMesh Guardian.

Implements the unified 6-stage cognitive defense cycle:
  Observe -> Detect -> Analyse -> Explain -> Respond -> Learn
"""

import math
from typing import Dict, Any

from app.extractor import (
    normalize_input_text,
    extract_entities,
    create_tokenized_text,
)
from app.verifier import get_verifier
from app.model_loader import get_model_manager
from app.response_engine import (
    generate_explanation,
    generate_recommended_actions,
)


def calculate_entropy(probabilities: Dict[str, float]) -> float:
    """Calculates Shannon entropy to evaluate classification uncertainty."""
    ent = 0.0

    for p in probabilities.values():
        if p > 0:
            ent -= p * math.log2(p)

    return ent


def evaluate_heuristic_classification(
    text: str,
    tokenized: str,
) -> tuple:
    """Fallback classifier when the trained classifier is unavailable."""

    tl = text.lower()

    classes = [
        "legitimate",
        "phishing",
        "payment_or_credential_scam",
        "authority_impersonation_scam",
        "remote_access_scam",
        "UPI_QR_scam",
        "fake_payment_scam",
        "other_suspicious",
    ]

    scores = {c: 0.05 for c in classes}

    # Remote access scam signals
    if any(
        w in tl
        for w in [
            "remoteassistdemo",
            "supportdemo",
            "screenhelpdemo",
            "anydesk",
            "quicksupport",
            "teamviewer",
            "screen share code",
            "remote connection prompt",
        ]
    ):
        scores["remote_access_scam"] += 0.85

    # Authority impersonation / digital arrest signals
    if any(
        w in tl
        for w in [
            "digital arrest",
            "digital custody",
            "arrest warrant",
            "customs",
            "cyber office",
            "cbi",
            "supreme court",
            "special crime",
            "non-bailable",
            "power connection will be cut",
            "deactivation within 2 hours",
        ]
    ):
        scores["authority_impersonation_scam"] += 0.85

    # UPI / QR collect scam
    if any(
        w in tl
        for w in [
            "upi pin to receive",
            "upi pin daaliye",
            "enter your 6-digit upi pin",
            "cashback receive",
            "lottery me",
            "upi collect request",
        ]
    ):
        scores["UPI_QR_scam"] += 0.85

    # Fake payment receipt scam
    if any(
        w in tl
        for w in [
            "payment approved to merchant",
            "payment successful! rs",
            "goods release madi",
            "screenshot dekh lijiye",
            "held in escrow",
        ]
    ):
        scores["fake_payment_scam"] += 0.80

    # Phishing / credential harvesting
    if any(
        w in tl
        for w in [
            "reactivate-card",
            "kyc-update",
            "instant-loan",
            "bank-unblock",
            "utility-refund",
            "enter your 16-digit",
            "mailbox has exceeded",
            "update-cert",
        ]
    ):
        scores["payment_or_credential_scam"] += 0.75
        scores["phishing"] += 0.70

    # Legitimate transactional anchors
    is_legitimate_otp = (
        "otp" in tl
        and any(
            w in tl
            for w in [
                "never share",
                "kisi ke sath share na karein",
                "do not share",
                "yavathoo otp kelolla",
                "bank will never call asking",
            ]
        )
    )

    is_legitimate_salary = (
        "credited" in tl
        and any(
            w in tl
            for w in [
                "salary",
                "employer",
                "available balance",
            ]
        )
    )

    is_legitimate_statement = any(
        w in tl
        for w in [
            "monthly statement",
            "routine maintenance",
            "tuition fee payment",
            "official seva kendra",
            "periodic kyc updation",
            "original aadhaar and pan",
        ]
    )

    if (
        is_legitimate_otp
        or is_legitimate_salary
        or is_legitimate_statement
    ):
        scores["legitimate"] += 0.90

    total = sum(scores.values())

    probs = {
        k: round(v / total, 4)
        for k, v in scores.items()
    }

    pred_label = max(probs, key=probs.get)

    return pred_label, probs


def evaluate_heuristic_tactics(text: str) -> Dict[str, float]:
    """Fallback tactic detector when the trained tactic model is unavailable."""

    tl = text.lower()

    tactics = {
        "authority_impersonation": 0.0,
        "urgency": 0.0,
        "fear_or_threat": 0.0,
        "secrecy": 0.0,
        "isolation": 0.0,
        "payment_request": 0.0,
        "otp_request": 0.0,
        "credential_request": 0.0,
        "remote_access_request": 0.0,
        "screen_share_request": 0.0,
        "upi_collect_request": 0.0,
    }

    if any(
        w in tl
        for w in [
            "inspector",
            "officer",
            "police",
            "customs",
            "cyber office",
            "cbi",
            "supreme court",
            "enforcement",
            "bank official",
        ]
    ):
        tactics["authority_impersonation"] = 0.92

    if any(
        w in tl
        for w in [
            "immediately",
            "within 2 hours",
            "tonight",
            "urgent",
            "hurry",
            "expire today",
            "right now",
            "jaldi",
        ]
    ):
        tactics["urgency"] = 0.88

    if any(
        w in tl
        for w in [
            "arrest warrant",
            "fir",
            "block your account",
            "raid",
            "jail",
            "penalty",
            "disconnection",
            "line cut",
        ]
    ):
        tactics["fear_or_threat"] = 0.90

    if any(
        w in tl
        for w in [
            "do not tell anyone",
            "kisi ko batana mat",
            "confidential",
            "keep secret",
        ]
    ):
        tactics["secrecy"] = 0.85

    if any(
        w in tl
        for w in [
            "stay on video call",
            "closed room",
            "call disconnect mat karna",
            "stay on skype",
        ]
    ):
        tactics["isolation"] = 0.95

    if any(
        w in tl
        for w in [
            "transfer",
            "deposit",
            "send money",
            "penaltyfunds",
            "paisa bhej",
        ]
    ):
        tactics["payment_request"] = 0.82

    if "otp" in tl and any(
        w in tl
        for w in [
            "enter otp",
            "read out",
            "tell me otp",
            "batayein",
            "heli",
        ]
    ):
        tactics["otp_request"] = 0.89

    if any(
        w in tl
        for w in [
            "password",
            "card number",
            "cvv",
            "netbankingpassword",
            "login credentials",
        ]
    ):
        tactics["credential_request"] = 0.87

    if any(
        w in tl
        for w in [
            "remoteassistdemo",
            "supportdemo",
            "screenhelpdemo",
            "anydesk",
            "quicksupport",
            "teamviewer",
        ]
    ):
        tactics["remote_access_request"] = 0.96

    if any(
        w in tl
        for w in [
            "screen share",
            "read out code",
            "share your screen",
            "9-digit code",
        ]
    ):
        tactics["screen_share_request"] = 0.94

    if any(
        w in tl
        for w in [
            "upi pin to receive",
            "upi pin daaliye",
            "enter your secret upi pin",
            "claim cashback",
            "upi collect",
        ]
    ):
        tactics["upi_collect_request"] = 0.95

    return {
        k: round(v, 2)
        for k, v in tactics.items()
    }


def evaluate_tactics(
    text: str,
    tokenized: str,
    model_mgr,
) -> Dict[str, float]:
    """Predict manipulation tactics using the trained multi-label model.

    Falls back to the existing heuristic detector if the ML tactic
    model or embedding pipeline is unavailable.
    """

    if not model_mgr.tactic_model or not model_mgr.embedder:
        return evaluate_heuristic_tactics(text)

    try:
        embedding = model_mgr.embedder.encode(
            [tokenized],
            convert_to_numpy=True,
        )

        probabilities = model_mgr.tactic_model.predict_proba(
            embedding
        )

        tactics = model_mgr.get_tactics()

        tactic_scores = {}

        for index, tactic in enumerate(tactics):
            tactic_probability = probabilities[index]

            # MultiOutputClassifier returns one probability
            # array per tactic, shaped as (samples, classes).
            positive_probability = float(
                tactic_probability[0][1]
            )

            tactic_scores[tactic] = round(
            max(0.0, min(1.0, positive_probability)),
            4,
            )

        return tactic_scores

    except Exception:
        return evaluate_heuristic_tactics(text)


def analyze_communication(
    text: str,
    channel: str = "sms",
) -> Dict[str, Any]:
    """Executes the full pipeline:

    Ingestion -> Detection -> Analysis -> Explanation -> Response
    """

    # 1. OBSERVE
    clean_text = normalize_input_text(text)
    tokenized_text = create_tokenized_text(clean_text)

    # 2. ANALYSE (Entities & IOCs)
    entities = extract_entities(clean_text)

    verifier = get_verifier()
    verification = verifier.verify_ioc_signals(
        entities
    )

    # 3. DETECT
    model_mgr = get_model_manager()
    model_mgr.load_models_if_needed()

    if model_mgr.classifier and model_mgr.embedder:
        try:
            emb = model_mgr.embedder.encode(
                [tokenized_text]
            )

            probs_arr = model_mgr.classifier.predict_proba(
                emb
            )[0]

            classes = model_mgr.get_classes()

            probs = {
                classes[i]: round(
                    float(probs_arr[i]),
                    4,
                )
                for i in range(len(classes))
            }

            pred_label = max(
                probs,
                key=probs.get,
            )

        except Exception:
            pred_label, probs = evaluate_heuristic_classification(
                clean_text,
                tokenized_text,
            )
    else:
        pred_label, probs = evaluate_heuristic_classification(
            clean_text,
            tokenized_text,
        )

    # ML tactic detection with heuristic fallback.
    tactics = evaluate_tactics(
        clean_text,
        tokenized_text,
        model_mgr,
    )

    # Calculate uncertainty.
    entropy = calculate_entropy(probs)
    max_prob = probs[pred_label]

    if max_prob > 0.70 and entropy < 1.5:
        uncertainty = "low"
    elif max_prob > 0.45:
        uncertainty = "medium"
    else:
        uncertainty = "high"

    # 4. EXPLAIN
    explanation = generate_explanation(
        predicted_label=pred_label,
        tactics=tactics,
        entities=entities,
        verification=verification,
        channel=channel,
    )

    # 5. RESPOND
    recommended_actions = generate_recommended_actions(
        predicted_label=pred_label,
        tactics=tactics,
        entities=entities,
        verification=verification,
        channel=channel,
    )

    return {
        "classification": {
            "predicted_label": pred_label,
            "probabilities": probs,
        },
        "entities": entities,
        "tactics": tactics,
        "verification": verification,
        "explanation": explanation,
        "recommended_actions": recommended_actions,
        "uncertainty": uncertainty,
    }