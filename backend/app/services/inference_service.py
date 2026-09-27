"""Inference execution service for SentryMesh V4 binary fraud model.

Strictly runs the trained model pipeline, evaluates probability against the
dynamic threshold, computes real feature attribution, and generates explanation.
"""

from app.schemas import (
    TextAnalysisResponse,
    InputType,
    PredictedLabel,
    SafetyLevel
)
from app.services.model_loader import get_model_loader
from app.services.attribution_service import compute_model_attribution
from app.services.explanation_service import build_explanation


def compute_safety_level(prob: float, threshold: float) -> SafetyLevel:
    """Computes non-alarmist safety tier based on model probability and dynamic threshold."""
    if prob >= 0.80:
        return "high_risk"
    if prob >= threshold:
        return "suspicious_needs_verification"
    if prob >= (threshold - 0.10):
        return "uncertain_needs_verification"
    return "no_strong_risk_signal"


def analyze_text_content(text: str, input_type: InputType) -> TextAnalysisResponse:
    """Executes the full inference and explanation pipeline on raw text."""
    loader = get_model_loader()
    model = loader.model
    threshold = loader.selected_threshold

    # 1. Run model.predict_proba on the input text
    probabilities = model.predict_proba([text])

    # 2. Extract suspicious probability using dynamic class index
    suspicious_idx = loader.suspicious_class_index
    suspicious_prob = float(probabilities[0][suspicious_idx])
    rounded_prob = round(suspicious_prob, 4)

    # 3. Determine binary predicted_label
    predicted_label: PredictedLabel = (
        "suspicious" if rounded_prob >= threshold else "legitimate"
    )

    # 4. Determine 4-tier safety level
    safety_level = compute_safety_level(rounded_prob, threshold)

    # 5. Compute real linear feature attribution
    model_evidence = compute_model_attribution(model, text)

    # 6. Build plain-language explanation and recommended actions
    explanation, recommended_actions = build_explanation(
        safety_level=safety_level,
        suspicious_probability=rounded_prob,
        selected_threshold=threshold,
        evidence=model_evidence,
        input_type=input_type
    )

    privacy_notice = "SentryMesh analyzes only the text or audio you explicitly submit."
    disclaimer = (
        "This is a text-based risk assessment, not proof that a caller, "
        "message, payment request, or voice is safe or fraudulent."
    )

    return TextAnalysisResponse(
        module="parent_call_guardian",
        status="analyzed",
        predicted_label=predicted_label,
        suspicious_probability=rounded_prob,
        selected_threshold=threshold,
        safety_level=safety_level,
        input_type=input_type,
        model_evidence=model_evidence,
        explanation=explanation,
        recommended_actions=recommended_actions,
        privacy_notice=privacy_notice,
        disclaimer=disclaimer
    )
