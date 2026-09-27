"""
Train the SentryMesh WebGuard phishing classifier.

Dataset:
UCI PhiUSIIL Phishing URL (Website) Dataset

The model uses structural URL/webpage features and deliberately excludes
raw URL/domain/title strings to reduce memorization and leakage.
"""

from pathlib import Path

import joblib
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TRAIN_FILE = PROJECT_ROOT / "data" / "processed" / "webguard_train.csv"
TEST_FILE = PROJECT_ROOT / "data" / "processed" / "webguard_test.csv"

MODEL_DIR = PROJECT_ROOT / "models"
REPORT_DIR = PROJECT_ROOT / "reports"

MODEL_FILE = MODEL_DIR / "webguard_phiusiil_logreg.joblib"
METRICS_FILE = REPORT_DIR / "webguard_phiusiil_metrics.csv"


TARGET = "label"

EXCLUDED_COLUMNS = {
    "URL",
    "Domain",
    "Title",
    "TLD",
    "original_label",
    "label",
    "source_dataset",
    "source",
    "channel",
    "language",
}


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Select numeric and boolean structural features."""

    feature_columns = [
        column
        for column in df.columns
        if column not in EXCLUDED_COLUMNS
    ]

    X = df[feature_columns].copy()

    # Convert boolean-like values to numeric where possible.
    for column in X.columns:
        if X[column].dtype == "object":
            X[column] = pd.to_numeric(
                X[column],
                errors="coerce",
            )

    X = X.replace(
        [float("inf"), float("-inf")],
        pd.NA,
    )

    X = X.fillna(0)

    return X


def main() -> None:
    print("Loading WebGuard training data...")

    train_df = pd.read_csv(TRAIN_FILE)
    test_df = pd.read_csv(TEST_FILE)

    X_train = prepare_features(train_df)
    X_test = prepare_features(test_df)

    y_train = train_df[TARGET]
    y_test = test_df[TARGET]

    if list(X_train.columns) != list(X_test.columns):
        raise RuntimeError(
            "Training and testing feature columns do not match."
        )

    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows: {len(X_test)}")
    print(f"Features used: {len(X_train.columns)}")

    print()
    print("Features:")
    print(X_train.columns.tolist())

    pipeline = Pipeline(
        steps=[
            (
                "scaler",
                StandardScaler(),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=42,
                ),
            ),
        ]
    )

    print()
    print("Training WebGuard model...")

    pipeline.fit(
        X_train,
        y_train,
    )

    predictions = pipeline.predict(X_test)

    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro",
    )

    weighted_f1 = f1_score(
        y_test,
        predictions,
        average="weighted",
    )

    print()
    print("WebGuard evaluation")
    print("-------------------")
    print(f"Accuracy:    {accuracy:.4f}")
    print(f"Macro F1:    {macro_f1:.4f}")
    print(f"Weighted F1: {weighted_f1:.4f}")

    print()
    print("Classification report:")
    print(
        classification_report(
            y_test,
            predictions,
            digits=4,
        )
    )

    print("Confusion matrix:")
    print(confusion_matrix(y_test, predictions))

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        {
            "model": pipeline,
            "features": X_train.columns.tolist(),
            "dataset": "UCI_PhiUSIIL",
            "model_type": "standard_scaler_logistic_regression",
            "random_state": 42,
        },
        MODEL_FILE,
    )

    metrics = pd.DataFrame(
        [
            {
                "dataset": "UCI_PhiUSIIL",
                "train_rows": len(X_train),
                "test_rows": len(X_test),
                "features": len(X_train.columns),
                "accuracy": accuracy,
                "macro_f1": macro_f1,
                "weighted_f1": weighted_f1,
            }
        ]
    )

    metrics.to_csv(
        METRICS_FILE,
        index=False,
    )

    print()
    print(f"Model saved: {MODEL_FILE}")
    print(f"Metrics saved: {METRICS_FILE}")


if __name__ == "__main__":
    main()