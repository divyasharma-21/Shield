from pathlib import Path
import argparse
import json

import joblib


BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "sentrymesh_binary_tfidf_v4.joblib"
)

METRICS_PATH = (
    BASE_DIR
    / "reports"
    / "sentrymesh_binary_tfidf_v4_metrics.json"
)


def load_model_and_threshold():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"V4 model not found:\n{MODEL_PATH}"
        )

    if not METRICS_PATH.exists():
        raise FileNotFoundError(
            f"V4 metrics file not found:\n{METRICS_PATH}"
        )

    model = joblib.load(MODEL_PATH)

    with open(
        METRICS_PATH,
        "r",
        encoding="utf-8"
    ) as metrics_file:
        metrics = json.load(metrics_file)

    threshold = metrics.get(
        "selected_suspicious_threshold"
    )

    if threshold is None:
        raise ValueError(
            "selected_suspicious_threshold "
            "was not found in the V4 metrics file."
        )

    return model, float(threshold)


def get_suspicious_probability(model, text):
    probabilities = model.predict_proba([text])

    suspicious_index = list(
        model.classes_
    ).index("suspicious")

    return float(
        probabilities[0][suspicious_index]
    )


def get_safety_level(probability, threshold):
    if probability >= 0.80:
        return "high_risk"

    if probability >= threshold:
        return "suspicious_needs_verification"

    if probability >= threshold - 0.10:
        return "uncertain_needs_verification"

    return "no_strong_risk_signal"


def get_guidance(safety_level):
    guidance = {
        "high_risk": (
            "Strong scam indicators were detected. "
            "Do not send money, share OTPs, passwords, "
            "UPI PINs, or card details. Do not scan a "
            "payment QR code or install a remote-access app. "
            "Verify independently through an official "
            "website, app, or phone number."
        ),
        "suspicious_needs_verification": (
            "This message may be risky. Pause before acting. "
            "Do not share financial or security information. "
            "Do not approve a payment request, scan a payment "
            "QR code, or give screen-sharing or remote-access "
            "permission. Verify independently through an "
            "official channel."
        ),
        "uncertain_needs_verification": (
            "The message cannot be assessed confidently. "
            "Treat any request for money, OTPs, passwords, "
            "UPI PINs, QR payments, screen sharing, or remote "
            "access as high risk until independently verified."
        ),
        "no_strong_risk_signal": (
            "No strong scam signal was detected from this text. "
            "This is not a guarantee that the message or caller "
            "is safe. Never share OTPs, passwords, UPI PINs, "
            "or remote-device access with an unverified person."
        )
    }

    return guidance[safety_level]

def analyze_text(text):
    text = str(text).strip()

    if len(text) < 10:
        raise ValueError(
            "Please provide at least 10 characters of text."
        )

    model, threshold = load_model_and_threshold()

    suspicious_probability = (
        get_suspicious_probability(
            model,
            text
        )
    )

    safety_level = get_safety_level(
        suspicious_probability,
        threshold
    )

    predicted_label = (
        "suspicious"
        if suspicious_probability >= threshold
        else "legitimate"
    )

    return {
        "predicted_label": predicted_label,
        "suspicious_probability": round(
            suspicious_probability,
            4
        ),
        "selected_threshold": threshold,
        "safety_level": safety_level,
        "guidance": get_guidance(safety_level),
        "disclaimer": (
    "This is a text-based risk assessment, not proof "
    "that a message, caller, app, link, or payment "
    "request is safe or fraudulent."
)
    }


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Analyze text using the SentryMesh V4 "
            "binary safety model."
        )
    )

    parser.add_argument(
        "--text",
        required=True,
        help="Message or transcript text to analyze."
    )

    arguments = parser.parse_args()

    result = analyze_text(arguments.text)

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )


if __name__ == "__main__":
    main()