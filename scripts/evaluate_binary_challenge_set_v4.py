from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
)


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

CHALLENGE_PATH = (
    BASE_DIR
    / "data"
    / "samples"
    / "sentrymesh_challenge_test.csv"
)

RESULTS_PATH = (
    BASE_DIR
    / "reports"
    / "sentrymesh_binary_v4_challenge_results.csv"
)


def load_model_and_threshold():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "\nV4 model was not found.\n"
            f"Expected path:\n{MODEL_PATH}\n\n"
            "Run train_binary_model_v4.py first."
        )

    if not METRICS_PATH.exists():
        raise FileNotFoundError(
            "\nV4 metrics file was not found.\n"
            f"Expected path:\n{METRICS_PATH}\n\n"
            "Run train_binary_model_v4.py first."
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
            "The V4 metrics file does not contain "
            "selected_suspicious_threshold."
        )

    return model, float(threshold)


def load_challenge_dataset():
    if not CHALLENGE_PATH.exists():
        raise FileNotFoundError(
            "\nChallenge dataset was not found.\n"
            f"Expected path:\n{CHALLENGE_PATH}"
        )

    dataframe = pd.read_csv(CHALLENGE_PATH)

    required_columns = {
        "text",
        "label"
    }

    missing_columns = required_columns - set(
        dataframe.columns
    )

    if missing_columns:
        raise ValueError(
            "Challenge dataset is missing columns: "
            f"{sorted(missing_columns)}"
        )

    dataframe = dataframe.dropna(
        subset=["text", "label"]
    ).copy()

    dataframe["text"] = (
        dataframe["text"]
        .astype(str)
        .str.strip()
    )

    dataframe["label"] = (
        dataframe["label"]
        .astype(str)
        .str.strip()
    )

    dataframe = dataframe[
        dataframe["text"].str.len() >= 10
    ].copy()

    dataframe["actual_binary_label"] = (
        dataframe["label"].apply(
            lambda value: (
                "legitimate"
                if value.lower() == "legitimate"
                else "suspicious"
            )
        )
    )

    return dataframe


def get_suspicious_probabilities(model, texts):
    probabilities = model.predict_proba(texts)

    suspicious_index = list(
        model.classes_
    ).index("suspicious")

    return probabilities[:, suspicious_index]


def predicted_label_from_threshold(
    suspicious_probability,
    threshold
):
    if suspicious_probability >= threshold:
        return "suspicious"

    return "legitimate"


def safety_level(suspicious_probability, threshold):
    if suspicious_probability >= 0.80:
        return "high_risk"

    if suspicious_probability >= threshold:
        return "suspicious_needs_verification"

    if suspicious_probability >= threshold - 0.10:
        return "uncertain_needs_verification"

    return "no_strong_risk_signal"


def main():
    print("\nLoading binary SentryMesh V4 model...")

    model, threshold = load_model_and_threshold()

    print("Selected suspicious threshold:", threshold)

    print("\nLoading development challenge dataset...")

    dataframe = load_challenge_dataset()

    suspicious_probabilities = (
        get_suspicious_probabilities(
            model,
            dataframe["text"]
        )
    )

    dataframe["suspicious_probability"] = (
        suspicious_probabilities
    )

    dataframe["selected_threshold"] = threshold

    dataframe["predicted_binary_label"] = (
        dataframe[
            "suspicious_probability"
        ].apply(
            lambda value: (
                predicted_label_from_threshold(
                    value,
                    threshold
                )
            )
        )
    )

    dataframe["safety_level"] = dataframe[
        "suspicious_probability"
    ].apply(
        lambda value: safety_level(
            value,
            threshold
        )
    )

    y_true = dataframe["actual_binary_label"]
    y_pred = dataframe["predicted_binary_label"]

    print("\nBinary V4 Challenge Classification Report:\n")

    print(
        classification_report(
            y_true,
            y_pred,
            labels=[
                "legitimate",
                "suspicious"
            ],
            digits=4,
            zero_division=0
        )
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=[
            "legitimate",
            "suspicious"
        ]
    )

    print("\nConfusion Matrix:")
    print(matrix)

    dataframe["correct"] = (
        dataframe["actual_binary_label"]
        == dataframe["predicted_binary_label"]
    )

    total_examples = len(dataframe)

    correct_predictions = int(
        dataframe["correct"].sum()
    )

    wrong_predictions = int(
        (~dataframe["correct"]).sum()
    )

    print("\nTotal examples:", total_examples)

    print("Correct predictions:", correct_predictions)

    print("Wrong predictions:", wrong_predictions)

    print("\nSafety-level distribution:")

    print(
        dataframe["safety_level"].value_counts()
    )

    false_negatives = dataframe[
        (
            dataframe["actual_binary_label"]
            == "suspicious"
        )
        & (
            dataframe["predicted_binary_label"]
            == "legitimate"
        )
    ].copy()

    false_positives = dataframe[
        (
            dataframe["actual_binary_label"]
            == "legitimate"
        )
        & (
            dataframe["predicted_binary_label"]
            == "suspicious"
        )
    ].copy()

    output_columns = [
        "text",
        "label",
        "actual_binary_label",
        "predicted_binary_label",
        "suspicious_probability",
        "selected_threshold",
        "safety_level"
    ]

    print("\nFalse negatives:")
    print(
        "These are scams incorrectly predicted "
        "as legitimate."
    )

    if false_negatives.empty:
        print("\nNo false negatives found.")
    else:
        print(
            false_negatives[
                output_columns
            ].to_string(
                index=False
            )
        )

    print("\nFalse positives:")
    print(
        "These are legitimate messages incorrectly "
        "predicted as suspicious."
    )

    if false_positives.empty:
        print("\nNo false positives found.")
    else:
        print(
            false_positives[
                output_columns
            ].to_string(
                index=False
            )
        )

    RESULTS_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataframe.to_csv(
        RESULTS_PATH,
        index=False
    )

    print("\nSaved V4 challenge results to:")

    print(RESULTS_PATH)

    print("\nUser-facing safety rule:")

    print(
        "Never present no_strong_risk_signal as "
        "'definitely safe'."
    )

    print(
        "For any payment, OTP, password, QR, "
        "screen-sharing, remote-access, or urgent "
        "authority request, independently verify "
        "through an official channel."
    )


if __name__ == "__main__":
    main()