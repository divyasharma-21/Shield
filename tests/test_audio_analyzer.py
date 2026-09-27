from app.audio_analyzer import (
    analyze_audio_call,
    analyze_call_transcript,
    transcribe_audio,
)


def test_transcript_detects_otp_and_urgency():
    result = analyze_call_transcript(
        "This is urgent. Tell me your OTP immediately."
    )

    assert result["call_risk"] == "medium"
    assert "urgency" in result["detected_signals"]
    assert "otp_request" in result["detected_signals"]


def test_transcript_detects_payment_pressure():
    result = analyze_call_transcript(
        "You must transfer money right now to avoid a penalty."
    )

    assert "payment_pressure" in result["detected_signals"]
    assert "urgency" in result["detected_signals"]


def test_transcript_detects_remote_access():
    result = analyze_call_transcript(
        "Install AnyDesk and share your screen."
    )

    assert "remote_access" in result["detected_signals"]
    assert result["signal_scores"]["remote_access"] == 0.95


def test_transcript_detects_authority_impersonation():
    result = analyze_call_transcript(
        "I am a bank officer from the cyber crime department."
    )

    assert "authority_impersonation" in result["detected_signals"]


def test_multiple_signals_raise_call_risk():
    result = analyze_call_transcript(
        "This is urgent. I am a bank officer. "
        "Tell me your OTP and transfer money immediately."
    )

    assert result["call_risk"] == "high"
    assert len(result["detected_signals"]) >= 3
    assert result["possible_deepfake_call"] is True
    assert result["deepfake_confidence"] == "medium"


def test_normal_call_is_low_risk():
    result = analyze_call_transcript(
        "Hi, I am calling to confirm our meeting tomorrow afternoon."
    )

    assert result["call_risk"] == "low"
    assert result["detected_signals"] == []
    assert result["possible_deepfake_call"] is False


def test_empty_transcript():
    result = analyze_call_transcript("")

    assert result["transcript_available"] is False
    assert result["call_risk"] == "low"


def test_provided_transcript_takes_priority():
    result = analyze_audio_call(
        audio_path="does_not_exist.wav",
        transcript="This is urgent. Tell me your OTP."
    )

    assert result["input_type"] == "transcript"
    assert result["transcription"]["engine"] == "provided-transcript"
    assert result["transcription"]["success"] is True
    assert "otp_request" in result["analysis"]["detected_signals"]


def test_no_input_is_handled_safely():
    result = analyze_audio_call()

    assert result["input_type"] == "none"
    assert result["analysis"]["call_risk"] == "low"


def test_missing_audio_file_is_handled_safely():
    result = transcribe_audio("definitely_missing_audio_file.wav")

    assert result["success"] is False
    assert result["transcript"] == ""
    assert "not found" in result["error"].lower()


def test_deepfake_claim_is_conservative():
    result = analyze_call_transcript(
        "This is urgent. I am a bank officer. "
        "Tell me your OTP and transfer money now."
    )

    assert result["possible_deepfake_call"] is True

    note = result["deepfake_note"].lower()

    assert "cannot establish" in note
    assert "synthetic" in note