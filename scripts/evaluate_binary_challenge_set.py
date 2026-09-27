from pathlib import Path

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
    / "sentrymesh_binary_tfidf_v1.joblib"
)

CHALLENGE_PATH = (
    BASE_DIR
    / "data"
    / "samples"
    / "sentrymesh_challenge_test.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "reports"
    / "sentrymesh_binary_challenge_results.csv"
)


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Binary model not found:\n{MODEL_PATH}\n"
            "Run train_binary_model.py first."
        )

    if not CHALLENGE_PATH.exists():
        raise FileNotFoundError(
            f"Challenge dataset not found:\n{CHALLENGE_PATH}"
        )

    print("\nLoading binary SentryMesh model...")

    model = joblib.load(
        MODEL_PATH
    )

    print("Loading independent challenge dataset...")

    dataframe = pd.read_csv(
        CHALLENGE_PATH
    )

    required_columns = {
        "text",
        "label"
    }

    missing_columns = required_columns - set(
        dataframe.columns
    )

    if missing_columns:
        raise ValueError(
            f"Challenge CSV is missing: {missing_columns}"
        )

    dataframe = dataframe.dropna(
        subset=["text", "label"]
    ).copy()

    dataframe["expected_binary_label"] = dataframe[
        "label"
    ].apply(
        lambda value: (
            "legitimate"
            if str(value).strip().lower() == "legitimate"
            else "suspicious"
        )
    )

    predictions = model.predict(
        dataframe["text"]
    )

    probabilities = model.predict_proba(
        dataframe["text"]
    )

    dataframe["predicted_binary_label"] = predictions

    dataframe["prediction_confidence"] = probabilities.max(
        axis=1
    )

    dataframe["correct"] = (
        dataframe["expected_binary_label"]
        == dataframe["predicted_binary_label"]
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataframe.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nBinary Challenge Classification Report:\n")

    print(
        classification_report(
            dataframe["expected_binary_label"],
            dataframe["predicted_binary_label"],
            digits=4,
            zero_division=0
        )
    )

    print("\nConfusion Matrix:")

    print(
        confusion_matrix(
            dataframe["expected_binary_label"],
            dataframe["predicted_binary_label"],
            labels=[
                "legitimate",
                "suspicious"
            ]
        )
    )

    total_examples = len(dataframe)

    correct_examples = int(
        dataframe["correct"].sum()
    )

    wrong_examples = total_examples - correct_examples

    print("\nTotal examples:", total_examples)
    print("Correct predictions:", correct_examples)
    print("Wrong predictions:", wrong_examples)

    print("\nFalse negatives:")
    print(
        "These are scams incorrectly predicted as legitimate.\n"
    )

    false_negatives = dataframe[
        (dataframe["expected_binary_label"] == "suspicious")
        & (dataframe["predicted_binary_label"] == "legitimate")
    ]

    if false_negatives.empty:
        print("No false negatives found.")
    else:
        print(
            false_negatives[
                [
                    "text",
                    "label",
                    "predicted_binary_label",
                    "prediction_confidence"
                ]
            ].to_string(index=False)
        )

    print("\nFalse positives:")
    print(
        "These are legitimate messages incorrectly predicted as suspicious.\n"
    )

    false_positives = dataframe[
        (dataframe["expected_binary_label"] == "legitimate")
        & (dataframe["predicted_binary_label"] == "suspicious")
    ]

    if false_positives.empty:
        print("No false positives found.")
    else:
        print(
            false_positives[
                [
                    "text",
                    "label",
                    "predicted_binary_label",
                    "prediction_confidence"
                ]
            ].to_string(index=False)
        )

    print("\nSaved binary challenge results to:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()