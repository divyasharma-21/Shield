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
    / "sentrymesh_multiclass_v1.csv"
)

MODEL_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"

MODEL_PATH = MODEL_DIR / "sentrymesh_tfidf_v1.joblib"

METRICS_PATH = (
    REPORTS_DIR
    / "sentrymesh_tfidf_v1_metrics.json"
)

CONFUSION_MATRIX_PATH = (
    REPORTS_DIR
    / "sentrymesh_tfidf_v1_confusion_matrix.png"
)

WRONG_PREDICTIONS_PATH = (
    REPORTS_DIR
    / "sentrymesh_tfidf_v1_wrong_predictions.csv"
)


def load_dataset():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            "\nDataset file was not found.\n"
            f"Expected path:\n{DATA_PATH}\n\n"
            "Create the processed training CSV first."
        )

    dataframe = pd.read_csv(DATA_PATH)

    required_columns = {"text", "label"}

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            "\nDataset is missing required columns.\n"
            f"Missing: {sorted(missing_columns)}\n"
            "Required columns: text,label"
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

    if dataframe.empty:
        raise ValueError(
            "No valid rows remain after cleaning."
        )

    return dataframe


def save_confusion_matrix(y_true, y_pred, labels):
    matrix = confusion_matrix(
        y_true,
        y_pred,
        labels=labels
    )

    plt.figure(figsize=(12, 8))

    sns.heatmap(
        matrix,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels
    )

    plt.title(
        "SentryMesh TF-IDF Baseline Confusion Matrix"
    )

    plt.xlabel("Predicted Label")
    plt.ylabel("Actual Label")

    plt.xticks(rotation=45, ha="right")
    plt.yticks(rotation=0)

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

    print("\nLoading SentryMesh dataset...")

    dataframe = load_dataset()

    print("\nDataset shape:")
    print(dataframe.shape)

    print("\nDataset columns:")
    print(dataframe.columns.tolist())

    print("\nClass distribution:")

    label_counts = dataframe["label"].value_counts()

    print(label_counts)

    if len(label_counts) < 2:
        raise ValueError(
            "\nTraining requires at least two labels.\n"
            "For example: legitimate and suspicious."
        )

    if label_counts.min() < 2:
        raise ValueError(
            "\nEvery label needs at least two examples.\n"
            "Add more examples or merge rare labels."
        )

    X = dataframe["text"]
    y = dataframe["label"]

    print("\nSplitting training and test data...")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )

    print("Training samples:", len(X_train))
    print("Testing samples:", len(X_test))

    print("\nTraining TF-IDF + Logistic Regression model...")

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

    print("\nEvaluating on unseen test data...")

    predictions = model.predict(X_test)

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

    print("\nClassification Report:\n")

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

    print("\nSaving trained model...")

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

    wrong_predictions = prediction_results[
        prediction_results["actual_label"]
        != prediction_results["predicted_label"]
    ]

    wrong_predictions.to_csv(
        WRONG_PREDICTIONS_PATH,
        index=False
    )

    metrics = {
        "model_name": "sentrymesh_tfidf_v1",
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

    print("\nTraining completed successfully.")

    print("\nCreated files:")
    print(f"Model: {MODEL_PATH}")
    print(f"Metrics: {METRICS_PATH}")
    print(f"Confusion matrix: {CONFUSION_MATRIX_PATH}")
    print(f"Wrong predictions: {WRONG_PREDICTIONS_PATH}")


if __name__ == "__main__":
    main()