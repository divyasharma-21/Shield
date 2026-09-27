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
    precision_recall_fscore_support,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "sentrymesh_binary_v3.csv"
)

MODEL_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

MODEL_PATH = (
    MODEL_DIR
    / "sentrymesh_binary_tfidf_v3.joblib"
)

METRICS_PATH = (
    REPORTS_DIR
    / "sentrymesh_binary_tfidf_v3_metrics.json"
)

CONFUSION_MATRIX_PATH = (
    REPORTS_DIR
    / "sentrymesh_binary_tfidf_v3_confusion_matrix.png"
)

WRONG_PREDICTIONS_PATH = (
    REPORTS_DIR
    / "sentrymesh_binary_tfidf_v3_wrong_predictions.csv"
)


def load_dataset():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "\nBinary dataset was not found.\n"
            f"Expected path:\n{DATA_PATH}\n\n"
            "Run create_binary_dataset.py first."
        )

    dataframe = pd.read_csv(DATA_PATH)

    required_columns = {"text", "label"}

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"Dataset is missing columns: {sorted(missing_columns)}"
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
    ]

    dataframe = dataframe.drop_duplicates(
        subset=["text"]
    )

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
            f"Unexpected labels found: {unexpected_labels}\n"
            "Binary dataset must contain only legitimate and suspicious."
        )

    return dataframe


def save_confusion_matrix(y_true, y_pred, labels):
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
        "SentryMesh Binary Model Confusion Matrix"
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

    print("\nLoading binary SentryMesh dataset...")

    dataframe = load_dataset()

    print("\nDataset shape:")
    print(dataframe.shape)

    print("\nClass distribution:")
    print(
        dataframe["label"].value_counts()
    )

    X = dataframe["text"]
    y = dataframe["label"]

    print("\nSplitting train and test data...")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print("Training samples:", len(X_train))
    print("Testing samples:", len(X_test))

    print("\nTraining binary TF-IDF model...")

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
                    random_state=42
                )
            )
        ]
    )

    model.fit(
        X_train,
        y_train
    )

    print("\nModel training completed.")

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test,
        predictions,
        average="weighted",
        zero_division=0
    )

    print("\nBinary Classification Report:\n")

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

    print("\nSaving binary model...")

    joblib.dump(
        model,
        MODEL_PATH
    )

    labels = model.classes_.tolist()

    save_confusion_matrix(
        y_test,
        predictions,
        labels
    )

    prediction_results = pd.DataFrame(
        {
            "text": X_test.values,
            "actual_label": y_test.values,
            "predicted_label": predictions
        }
    )

    prediction_results["correct"] = (
        prediction_results["actual_label"]
        == prediction_results["predicted_label"]
    )

    wrong_predictions = prediction_results[
        ~prediction_results["correct"]
    ]

    wrong_predictions.to_csv(
        WRONG_PREDICTIONS_PATH,
        index=False
    )

    metrics = {
        "model_name": "sentrymesh_binary_tfidf_v3",
        "dataset_path": str(DATA_PATH),
        "total_samples": int(len(dataframe)),
        "training_samples": int(len(X_train)),
        "testing_samples": int(len(X_test)),
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

    print("\nBinary model training completed successfully.")

    print("\nCreated files:")
    print(f"Model: {MODEL_PATH}")
    print(f"Metrics: {METRICS_PATH}")
    print(f"Confusion Matrix: {CONFUSION_MATRIX_PATH}")
    print(f"Wrong Predictions: {WRONG_PREDICTIONS_PATH}")


if __name__ == "__main__":
    main()
