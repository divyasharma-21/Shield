from app.parent_guardian_safety import (
    detect_parent_guardian_patterns,
    has_parent_guardian_risk,
    get_parent_guardian_recommendations,
)


def test_location_monitoring_detection():
    result = detect_parent_guardian_patterns(
        "Your location is shared with me."
    )

    assert result["detected"] is True
    assert result["risk_level"] == "high"
    assert "location_monitoring" in result["patterns"]


def test_phone_monitoring_detection():
    result = detect_parent_guardian_patterns(
        "I am checking your phone."
    )

    assert result["detected"] is True
    assert "phone_monitoring" in result["patterns"]


def test_social_isolation_detection():
    result = detect_parent_guardian_patterns(
        "You must not talk to strangers."
    )

    assert result["detected"] is True
    assert "social_isolation" in result["patterns"]


def test_social_reporting_detection():
    result = detect_parent_guardian_patterns(
        "Report every friend you make."
    )

    assert result["detected"] is True
    assert "social_reporting" in result["patterns"]


def test_movement_control_detection():
    result = detect_parent_guardian_patterns(
        "Never leave the house without me."
    )

    assert result["detected"] is True
    assert "movement_control" in result["patterns"]


def test_multiple_patterns_are_detected():
    result = detect_parent_guardian_patterns(
        "I am checking your phone. Your location is shared. "
        "Never leave the house without me."
    )

    assert result["detected"] is True
    assert len(result["patterns"]) == 3
    assert result["risk_level"] == "high"
    assert result["score"] > 0.90


def test_normal_parent_message_is_not_flagged():
    result = detect_parent_guardian_patterns(
        "Please call me when you reach home safely."
    )

    assert result["detected"] is False
    assert result["risk_level"] == "none"
    assert result["score"] == 0.0
    assert result["patterns"] == []


def test_empty_text_is_safe():
    result = detect_parent_guardian_patterns("")

    assert result["detected"] is False
    assert result["risk_level"] == "none"


def test_helper_function():
    assert has_parent_guardian_risk(
        "I am checking your phone."
    ) is True

    assert has_parent_guardian_risk(
        "Have a good day."
    ) is False


def test_recommendations_are_conservative():
    result = detect_parent_guardian_patterns(
        "Your location is shared."
    )

    recommendations = get_parent_guardian_recommendations(result)

    assert len(recommendations) >= 3
    assert any("context" in item.lower() for item in recommendations)


def test_no_criminal_or_abuse_accusation():
    result = detect_parent_guardian_patterns(
        "I am checking your phone."
    )

    text = str(result).lower()

    assert "criminal" not in text
    assert "abuser" not in text
    assert "abusive" not in text