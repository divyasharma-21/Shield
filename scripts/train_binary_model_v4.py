from pathlib import Path
import json

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    fbeta_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "sentrymesh_binary_v4.csv"
)

MODEL_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

MODEL_PATH = (
    MODEL_DIR
    / "sentrymesh_binary_tfidf_v4.joblib"
)

METRICS_PATH = (
    REPORTS_DIR
    / "sentrymesh_binary_tfidf_v4_metrics.json"
)

CONFUSION_MATRIX_PATH = (
    REPORTS_DIR
    / "sentrymesh_binary_tfidf_v4_confusion_matrix.png"
)

WRONG_PREDICTIONS_PATH = (
    REPORTS_DIR
    / "sentrymesh_binary_tfidf_v4_wrong_predictions.csv"
)

THRESHOLD_RESULTS_PATH = (
    REPORTS_DIR
    / "sentrymesh_binary_tfidf_v4_threshold_results.csv"
)

RANDOM_STATE = 42

TEST_SIZE = 0.20
VALIDATION_SIZE_OF_REMAINING = 0.20

THRESHOLD_VALUES = [
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
    0.65,
    0.70,
]


def load_dataset():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "\nBinary V4 dataset was not found.\n"
            f"Expected path:\n{DATA_PATH}\n\n"
            "Run create_binary_v4_dataset.py first."
        )

    dataframe = pd.read_csv(DATA_PATH)

    required_columns = {
        "text",
        "label"
    }

    missing_columns = required_columns - set(
        dataframe.columns
    )

    if missing_columns:
        raise ValueError(
            f"Dataset is missing columns: "
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

    dataframe = dataframe.drop_duplicates(
        subset=["text"]
    ).copy()

    valid_labels = {
        "legitimate",
        "suspicious"
    }

    found_labels = set(
        dataframe["label"].unique()
    )

    unexpected_labels = found_labels - valid_labels

    if unexpected_labels:
        raise ValueError(
            f"Unexpected labels found: "
            f"{sorted(unexpected_labels)}"
        )

    return dataframe


def get_suspicious_probabilities(model, texts):
    probabilities = model.predict_proba(texts)

    suspicious_index = list(
        model.classes_
    ).index("suspicious")

    return probabilities[:, suspicious_index]


def labels_from_threshold(
    suspicious_probabilities,
    threshold
):
    return [
        (
            "suspicious"
            if probability >= threshold
            else "legitimate"
        )
        for probability in suspicious_probabilities
    ]


def select_threshold(
    y_validation,
    suspicious_probabilities
):
    threshold_rows = []

    for threshold in THRESHOLD_VALUES:
        predictions = labels_from_threshold(
            suspicious_probabilities,
            threshold
        )

        precision, recall, f1, _ = (
            precision_recall_fscore_support(
                y_validation,
                predictions,
                labels=["suspicious"],
                average=None,
                zero_division=0
            )
        )

        f2 = fbeta_score(
            y_validation,
            predictions,
            pos_label="suspicious",
            beta=2,
            zero_division=0
        )

        false_negatives = sum(
            (
                actual == "suspicious"
                and predicted == "legitimate"
            )
            for actual, predicted in zip(
                y_validation,
                predictions
            )
        )

        false_positives = sum(
            (
                actual == "legitimate"
                and predicted == "suspicious"
            )
            for actual, predicted in zip(
                y_validation,
                predictions
            )
        )

        threshold_rows.append(
            {
                "threshold": threshold,
                "suspicious_precision": float(
                    precision[0]
                ),
                "suspicious_recall": float(
                    recall[0]
                ),
                "suspicious_f1": float(
                    f1[0]
                ),
                "suspicious_f2": float(f2),
                "false_negatives": int(
                    false_negatives
                ),
                "false_positives": int(
                    false_positives
                )
            }
        )

    threshold_dataframe = pd.DataFrame(
        threshold_rows
    )

    eligible = threshold_dataframe[
        threshold_dataframe[
            "suspicious_recall"
        ] >= 0.95
    ].copy()

    if not eligible.empty:
        selected_row = eligible.sort_values(
            by=[
            "suspicious_f2",
            "false_negatives",
            "false_positives",
            "threshold"
            ],
            ascending=[
            False,
            True,
            True,
            False
            ]
        ).iloc[0]
    else:
        selected_row = threshold_dataframe.sort_values(
            by=[
                "suspicious_f2",
                "false_negatives",
                "threshold"
            ],
            ascending=[
                False,
                True,
                False
            ]
        ).iloc[0]

    return threshold_dataframe, selected_row


def safety_level(probability, threshold):
    if probability >= 0.80:
        return "high_risk"

    if probability >= threshold:
        return "suspicious_needs_verification"

    if probability >= threshold - 0.10:
        return "uncertain_needs_verification"

    return "no_strong_risk_signal"


def save_confusion_matrix(
    y_true,
    y_pred,
    labels
):
    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels
    )

    plt.figure(figsize=(7, 5))

    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels
    )

    plt.title(
        "SentryMesh Binary V4 Confusion Matrix"
    )

    plt.xlabel("Predicted Label")
    plt.ylabel("Actual Label")

    plt.tight_layout()

    plt.savefig(
        CONFUSION_MATRIX_PATH,
        dpi=200
    )

    plt.close()


def main():
    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\nLoading binary SentryMesh V4 dataset...")

    dataframe = load_dataset()

    print("\nDataset shape:")
    print(dataframe.shape)

    print("\nClass distribution:")
    print(
        dataframe["label"].value_counts()
    )

    X = dataframe["text"]
    y = dataframe["label"]

    print("\nCreating train, validation, and test splits...")

    X_remaining, X_test, y_remaining, y_test = (
        train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=y
        )
    )

    X_train, X_validation, y_train, y_validation = (
        train_test_split(
            X_remaining,
            y_remaining,
            test_size=VALIDATION_SIZE_OF_REMAINING,
            random_state=RANDOM_STATE,
            stratify=y_remaining
        )
    )

    print("Training samples:", len(X_train))
    print("Validation samples:", len(X_validation))
    print("Testing samples:", len(X_test))

    print("\nTraining binary TF-IDF V4 model...")

    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=1,
                    max_features=50000,
                    sublinear_tf=True
                )
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=3000,
                    class_weight="balanced",
                    random_state=RANDOM_STATE
                )
            )
        ]
    )

    model.fit(
        X_train,
        y_train
    )

    print("\nSelecting safety-first threshold "
          "on validation data...")

    validation_probabilities = (
        get_suspicious_probabilities(
            model,
            X_validation
        )
    )

    threshold_dataframe, selected_row = (
        select_threshold(
            y_validation,
            validation_probabilities
        )
    )

    threshold_dataframe.to_csv(
        THRESHOLD_RESULTS_PATH,
        index=False
    )

    selected_threshold = float(
        selected_row["threshold"]
    )

    print("\nThreshold evaluation:")
    print(
        threshold_dataframe.to_string(
            index=False
        )
    )

    print("\nSelected suspicious threshold:")
    print(round(selected_threshold, 2))

    print("\nEvaluating once on held-out "
          "internal test data...")

    test_probabilities = get_suspicious_probabilities(
        model,
        X_test
    )

    predictions = labels_from_threshold(
        test_probabilities,
        selected_threshold
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision, recall, f1, _ = (
        precision_recall_fscore_support(
            y_test,
            predictions,
            average="weighted",
            zero_division=0
        )
    )

    print("\nBinary V4 Classification Report:\n")

    print(
        classification_report(
            y_test,
            predictions,
            digits=4,
            zero_division=0
        )
    )

    print("Accuracy:", round(accuracy, 4))
    print("Weighted Precision:", round(precision, 4))
    print("Weighted Recall:", round(recall, 4))
    print("Weighted F1 Score:", round(f1, 4))

    print("\nSaving binary V4 model and reports...")

    joblib.dump(
        model,
        MODEL_PATH
    )

    labels = [
        "legitimate",
        "suspicious"
    ]

    save_confusion_matrix(
        y_test,
        predictions,
        labels
    )

    prediction_results = pd.DataFrame(
        {
            "text": X_test.values,
            "actual_label": y_test.values,
            "predicted_label": predictions,
            "suspicious_probability": test_probabilities
        }
    )

    prediction_results["selected_threshold"] = (
        selected_threshold
    )

    prediction_results["safety_level"] = (
        prediction_results[
            "suspicious_probability"
        ].apply(
            lambda value: safety_level(
                value,
                selected_threshold
            )
        )
    )

    prediction_results["correct"] = (
        prediction_results["actual_label"]
        == prediction_results["predicted_label"]
    )

    wrong_predictions = prediction_results[
        ~prediction_results["correct"]
    ].copy()

    wrong_predictions.to_csv(
        WRONG_PREDICTIONS_PATH,
        index=False
    )

    metrics = {
        "model_name": "sentrymesh_binary_tfidf_v4",
        "dataset_path": str(DATA_PATH),
        "total_samples": int(len(dataframe)),
        "training_samples": int(len(X_train)),
        "validation_samples": int(
            len(X_validation)
        ),
        "testing_samples": int(len(X_test)),
        "selected_suspicious_threshold": (
            selected_threshold
        ),
        "threshold_selection": (
        "validation_f2_maximization_with_"
        "95_percent_suspicious_recall_minimum"
        ),
        "accuracy": float(accuracy),
        "weighted_precision": float(precision),
        "weighted_recall": float(recall),
        "weighted_f1": float(f1),
        "labels": labels
    }

    with open(
        METRICS_PATH,
        "w",
        encoding="utf-8"
    ) as metrics_file:
        json.dump(
            metrics,
            metrics_file,
            indent=2,
            ensure_ascii=False
        )

    print("\nBinary V4 model training completed "
          "successfully.")

    print("\nCreated files:")
    print(f"Model: {MODEL_PATH}")
    print(f"Metrics: {METRICS_PATH}")
    print(
        "Threshold results: "
        f"{THRESHOLD_RESULTS_PATH}"
    )
    print(
        "Confusion Matrix: "
        f"{CONFUSION_MATRIX_PATH}"
    )
    print(
        "Wrong Predictions: "
        f"{WRONG_PREDICTIONS_PATH}"
    )


if __name__ == "__main__":
    main()