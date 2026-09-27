from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import classification_report, confusion_matrix


BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "sentrymesh_tfidf_v1.joblib"
)

CHALLENGE_DATA_PATH = (
    BASE_DIR
    / "data"
    / "samples"
    / "sentrymesh_challenge_test.csv"
)

REPORT_PATH = (
    BASE_DIR
    / "reports"
    / "sentrymesh_challenge_results.csv"
)


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model was not found:\n{MODEL_PATH}\n"
            "Run train_tfidf_baseline.py first."
        )

    if not CHALLENGE_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Challenge file was not found:\n{CHALLENGE_DATA_PATH}"
        )

    print("\nLoading trained SentryMesh model...")
    model = joblib.load(MODEL_PATH)

    print("Loading challenge dataset...")
    dataframe = pd.read_csv(CHALLENGE_DATA_PATH)

    required_columns = {"text", "label"}

    if not required_columns.issubset(dataframe.columns):
        raise ValueError(
            "Challenge CSV must contain text and label columns."
        )

    dataframe = dataframe.dropna(
        subset=["text", "label"]
    ).copy()

    predictions = model.predict(
        dataframe["text"]
    )

    dataframe["predicted_label"] = predictions
    dataframe["correct"] = (
        dataframe["label"]
        == dataframe["predicted_label"]
    )

    probabilities = model.predict_proba(
        dataframe["text"]
    )

    dataframe["prediction_confidence"] = probabilities.max(
        axis=1
    )

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataframe.to_csv(
        REPORT_PATH,
        index=False
    )

    print("\nChallenge-set Classification Report:\n")

    print(
        classification_report(
            dataframe["label"],
            dataframe["predicted_label"],
            zero_division=0
        )
    )

    print("\nConfusion Matrix:\n")

    print(
        confusion_matrix(
            dataframe["label"],
            dataframe["predicted_label"],
            labels=model.classes_
        )
    )

    print("\nTotal challenge examples:", len(dataframe))
    print(
        "Correct predictions:",
        int(dataframe["correct"].sum())
    )
    print(
        "Wrong predictions:",
        int((~dataframe["correct"]).sum())
    )

    print("\nWrong predictions:\n")

    wrong_predictions = dataframe[
        ~dataframe["correct"]
    ]

    if wrong_predictions.empty:
        print("No wrong predictions found.")
    else:
        print(
            wrong_predictions[
                [
                    "text",
                    "label",
                    "predicted_label",
                    "prediction_confidence"
                ]
            ].to_string(index=False)
        )

    print("\nSaved challenge results to:")
    print(REPORT_PATH)


if __name__ == "__main__":
    main()