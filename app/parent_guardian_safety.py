"""
Parent / Guardian Safety Detection for SentryMesh.

Detects potentially high-risk monitoring, control, isolation, and
surveillance language in communications.

Important:
- This module identifies communication patterns, not people.
- It does not determine whether a sender is abusive, criminal, or unsafe.
- Results should be treated as safety signals requiring context.
"""

import re
from typing import Any, Dict, List


# Patterns represent communication signals, not conclusions about intent.
MONITORING_PATTERNS = {
    "location_monitoring": [
        r"\byour location is shared\b",
        r"\bshare your location\b",
        r"\bsend me your location\b",
        r"\bi can see your location\b",
        r"\bkeep your location on\b",
        r"\bturn on location sharing\b",
    ],
    "phone_monitoring": [
        r"\bi am checking your phone\b",
        r"\bi'm checking your phone\b",
        r"\blet me check your phone\b",
        r"\bgive me your phone\b",
        r"\bshow me your phone\b",
        r"\bi will check your phone\b",
    ],
    "social_isolation": [
        r"\byou must not talk to strangers\b",
        r"\bdon't talk to strangers\b",
        r"\bdo not talk to strangers\b",
        r"\bdon't talk to anyone\b",
        r"\bdo not talk to anyone\b",
        r"\bstop talking to your friends\b",
        r"\bdon't talk to your friends\b",
        r"\bdo not talk to your friends\b",
    ],
    "social_reporting": [
        r"\breport every friend\b",
        r"\breport all your friends\b",
        r"\btell me about every friend\b",
        r"\btell me who you talk to\b",
        r"\btell me everyone you talk to\b",
        r"\bi want to know who you talk to\b",
    ],
    "movement_control": [
        r"\bnever leave the house without me\b",
        r"\bdon't leave the house without me\b",
        r"\bdo not leave the house without me\b",
        r"\byou cannot leave the house\b",
        r"\byou can't leave the house\b",
        r"\bdon't go anywhere without me\b",
        r"\bdo not go anywhere without me\b",
    ],
}


RISK_SCORES = {
    "location_monitoring": 0.90,
    "phone_monitoring": 0.90,
    "social_isolation": 0.85,
    "social_reporting": 0.85,
    "movement_control": 0.90,
}


def _normalize_text(text: str) -> str:
    """Normalize text for case-insensitive pattern detection."""
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_parent_guardian_patterns(text: str) -> Dict[str, Any]:
    """
    Detect potentially high-risk monitoring/control patterns.

    Returns structured safety signals. A detected pattern does not establish
    abuse, criminal behavior, or harmful intent.
    """
    normalized_text = _normalize_text(text)

    detected_patterns: List[str] = []
    matched_phrases: List[str] = []
    pattern_scores: Dict[str, float] = {}

    for pattern_name, patterns in MONITORING_PATTERNS.items():
        for pattern in patterns:
            match = re.search(pattern, normalized_text)

            if match:
                if pattern_name not in detected_patterns:
                    detected_patterns.append(pattern_name)
                    pattern_scores[pattern_name] = RISK_SCORES[pattern_name]

                phrase = match.group(0)
                if phrase not in matched_phrases:
                    matched_phrases.append(phrase)

    if not detected_patterns:
        risk_level = "none"
        overall_score = 0.0
    elif len(detected_patterns) == 1:
        risk_level = "high"
        overall_score = pattern_scores[detected_patterns[0]]
    else:
        risk_level = "high"
        overall_score = min(
            1.0,
            max(pattern_scores.values()) + (0.05 * (len(detected_patterns) - 1)),
        )

    return {
        "detected": bool(detected_patterns),
        "risk_level": risk_level,
        "score": round(overall_score, 2),
        "patterns": detected_patterns,
        "matched_phrases": matched_phrases,
        "uncertainty": "medium" if detected_patterns else "low",
        "note": (
            "This result identifies monitoring or control language patterns "
            "and does not determine a person's intent, identity, or behavior."
        ),
    }


def has_parent_guardian_risk(text: str) -> bool:
    """Return True when at least one monitoring/control pattern is detected."""
    result = detect_parent_guardian_patterns(text)
    return result["detected"]


def get_parent_guardian_recommendations(
    detection_result: Dict[str, Any],
) -> List[str]:
    """
    Return conservative safety actions based on detected communication patterns.
    """
    if not detection_result.get("detected", False):
        return []

    return [
        "Consider the surrounding context before drawing conclusions.",
        "If the communication makes you feel unsafe or pressured, preserve the message.",
        "Consider speaking with a trusted person about the situation.",
        "If there is immediate danger, contact an appropriate local emergency or support service.",
    ]