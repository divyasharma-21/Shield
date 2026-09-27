"""
Audio and call-safety analysis for SentryMesh.

This module supports:
1. Existing call transcripts.
2. Audio transcription through Whisper when available.
3. Scam-pattern analysis of the resulting transcript.
4. A conservative possible-deepfake signal.

Important:
- A deepfake cannot be established from scam language alone.
- Scam-like language and synthetic-voice indicators are safety signals.
- The module never identifies a caller as a criminal.
"""

import re
from pathlib import Path
from typing import Any, Dict, Optional


SCAM_SIGNAL_PATTERNS = {
    "urgency": [
        "urgent",
        "immediately",
        "right now",
        "within 2 hours",
        "within two hours",
        "act now",
        "hurry",
        "do it now",
    ],
    "otp_request": [
        "otp",
        "one time password",
        "verification code",
        "tell me the code",
        "read out the code",
        "share the code",
    ],
    "payment_pressure": [
        "transfer money",
        "send money",
        "make the payment",
        "pay now",
        "deposit",
        "penalty",
        "fine",
        "pay the amount",
    ],
    "remote_access": [
        "anydesk",
        "teamviewer",
        "quicksupport",
        "remote access",
        "screen share",
        "share your screen",
        "install this app",
    ],
    "authority_impersonation": [
        "police",
        "cbi",
        "customs",
        "bank officer",
        "bank official",
        "government officer",
        "cyber crime",
        "income tax officer",
    ],
    "fear_or_threat": [
        "arrest",
        "warrant",
        "jail",
        "account will be blocked",
        "account will be frozen",
        "legal action",
        "penalty",
        "fir",
    ],
}


def _normalize_transcript(transcript: str) -> str:
    """Normalize transcript text for analysis."""
    if not isinstance(transcript, str):
        return ""

    return " ".join(transcript.lower().split())


def _contains_phrase(text: str, phrase: str) -> bool:
    """
    Match a signal as a complete word/phrase rather than a substring.

    This prevents short signals such as 'fir' from matching words such as
    'confirm'.
    """
    pattern = r"\b" + re.escape(phrase) + r"\b"
    return re.search(pattern, text) is not None


def transcribe_audio(audio_path: str) -> Dict[str, Any]:
    """
    Transcribe an audio file using Whisper when available.

    Whisper is imported lazily so SentryMesh can still analyze an existing
    transcript without requiring Whisper to be installed.
    """
    path = Path(audio_path)

    if not path.exists():
        return {
            "success": False,
            "transcript": "",
            "error": "Audio file was not found.",
            "engine": None,
        }

    try:
        import whisper

        model = whisper.load_model("tiny")
        result = model.transcribe(str(path))

        transcript = result.get("text", "").strip()

        return {
            "success": True,
            "transcript": transcript,
            "error": None,
            "engine": "whisper-tiny",
        }

    except ImportError:
        return {
            "success": False,
            "transcript": "",
            "error": "Whisper is not installed. Provide a transcript instead.",
            "engine": None,
        }

    except Exception as exc:
        return {
            "success": False,
            "transcript": "",
            "error": f"Audio transcription failed: {exc}",
            "engine": "whisper-tiny",
        }


def analyze_call_transcript(transcript: str) -> Dict[str, Any]:
    """
    Analyze a call transcript for scam-related communication signals.

    The deepfake signal is intentionally conservative:
    scam-like language can increase suspicion, but language alone cannot
    prove that a voice is synthetic.
    """
    normalized = _normalize_transcript(transcript)

    detected_signals = []
    signal_scores: Dict[str, float] = {}
    matched_phrases: Dict[str, list] = {}

    for signal_name, phrases in SCAM_SIGNAL_PATTERNS.items():
        matches = [
            phrase
            for phrase in phrases
            if _contains_phrase(normalized, phrase)
        ]

        if matches:
            detected_signals.append(signal_name)
            matched_phrases[signal_name] = matches

    if "urgency" in detected_signals:
        signal_scores["urgency"] = 0.85

    if "otp_request" in detected_signals:
        signal_scores["otp_request"] = 0.90

    if "payment_pressure" in detected_signals:
        signal_scores["payment_pressure"] = 0.88

    if "remote_access" in detected_signals:
        signal_scores["remote_access"] = 0.95

    if "authority_impersonation" in detected_signals:
        signal_scores["authority_impersonation"] = 0.90

    if "fear_or_threat" in detected_signals:
        signal_scores["fear_or_threat"] = 0.90

    scam_signal_count = len(detected_signals)

    if scam_signal_count >= 3:
        call_risk = "high"
    elif scam_signal_count >= 1:
        call_risk = "medium"
    else:
        call_risk = "low"

    # Transcript content alone cannot prove that a voice is synthetic.
    possible_deepfake = scam_signal_count >= 3

    if possible_deepfake:
        deepfake_confidence = "medium"
    else:
        deepfake_confidence = "low"

    return {
        "transcript_available": bool(normalized),
        "call_risk": call_risk,
        "detected_signals": detected_signals,
        "signal_scores": signal_scores,
        "matched_phrases": matched_phrases,
        "possible_deepfake_call": possible_deepfake,
        "deepfake_confidence": deepfake_confidence,
        "deepfake_note": (
            "This is only a possible deepfake-call signal. "
            "Transcript content alone cannot establish that a voice is synthetic."
        ),
    }


def analyze_audio_call(
    audio_path: Optional[str] = None,
    transcript: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze either a supplied transcript or an audio file.

    A supplied transcript takes priority, avoiding unnecessary transcription.
    """
    transcription = {
        "success": False,
        "transcript": "",
        "error": None,
        "engine": None,
    }

    if transcript is not None:
        final_transcript = transcript

        transcription["success"] = True
        transcription["transcript"] = transcript
        transcription["engine"] = "provided-transcript"

    elif audio_path:
        transcription = transcribe_audio(audio_path)
        final_transcript = transcription["transcript"]

    else:
        final_transcript = ""

    analysis = analyze_call_transcript(final_transcript)

    return {
        "input_type": (
            "transcript"
            if transcript is not None
            else "audio"
            if audio_path
            else "none"
        ),
        "transcription": transcription,
        "analysis": analysis,
    }