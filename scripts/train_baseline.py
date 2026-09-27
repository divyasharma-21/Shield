"""
Train the SentryMesh baseline text classifier.

Pipeline:
    Multiclass dataset
        -> SentenceTransformer embeddings
        -> LogisticRegression
        -> classifier.joblib
        -> label_mapping.json

The classifier learns from labeled examples. Scam classification is NOT
performed by keyword rules in this training script.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = BASE_DIR / "models"

DEFAULT_DATASET = PROCESSED_DIR / "sentrymesh_multiclass_v1.csv"
TEST_DATASET_PATH = PROCESSED_DIR / "test.csv"
CLASSIFIER_PATH = MODELS_DIR / "classifier.joblib"
MAPPING_PATH = MODELS_DIR / "label_mapping.json"

EXPECTED_CLASSES = [
    "legitimate",
    "phishing",
    "payment_or_credential_scam",
    "authority_impersonation_scam",
    "remote_access_scam",
    "UPI_QR_scam",
    "fake_payment_scam",
    "other_suspicious",
]


def load_dataset(dataset_path: Path) -> pd.DataFrame:
    """Load and validate the multiclass training dataset."""

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Training dataset not found:\n{dataset_path}\n\n"
            "Create data/processed/sentrymesh_multiclass_v1.csv "
            "before running the training stage."
        )

    df = pd.read_csv(dataset_path)

    if df.empty:
        raise ValueError("The training dataset is empty.")

    required_columns = {"text", "label"}
    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Dataset is missing required columns: {sorted(missing)}"
        )

    df = df[["text", "label"]].copy()

    df["text"] = df["text"].fillna("").astype(str).str.strip()
    df["label"] = df["label"].fillna("").astype(str).str.strip()

    df = df[(df["text"] != "") & (df["label"] != "")].copy()

    if df.empty:
        raise ValueError(
            "No usable rows remain after removing empty text/labels."
        )

    return df


def validate_labels(df: pd.DataFrame) -> None:
    """Ensure the dataset contains the intended SentryMesh classes."""

    found_classes = sorted(df["label"].unique())
    expected = set(EXPECTED_CLASSES)
    found = set(found_classes)

    unexpected = found - expected
    missing = expected - found

    if unexpected:
        raise ValueError(
            "Dataset contains unsupported labels:\n"
            f"{sorted(unexpected)}"
        )

    if missing:
        raise ValueError(
            "Dataset does not yet contain all required SentryMesh classes.\n"
            f"Missing: {sorted(missing)}\n\n"
            "Do not train a partial classifier because the runtime expects "
            "the complete multiclass label mapping."
        )


def print_dataset_summary(df: pd.DataFrame) -> None:
    """Print a reproducible summary of the training data."""

    print("\n[INFO] Dataset summary")
    print(f"[INFO] Total usable records: {len(df)}")
    print("\n[INFO] Label distribution:")

    distribution = df["label"].value_counts().reindex(
        EXPECTED_CLASSES,
        fill_value=0,
    )

    for label, count in distribution.items():
        print(f"  {label}: {count}")


def create_embeddings(texts):
    """
    Generate multilingual SentenceTransformer embeddings.

    This uses the same embedding model as app/model_loader.py so the
    classifier receives the same feature representation during inference.
    """

    from sentence_transformers import SentenceTransformer

    model_name = (
        "sentence-transformers/"
        "paraphrase-multilingual-MiniLM-L12-v2"
    )

    print("\n[INFO] Loading embedding model:")
    print(f"[INFO] {model_name}")

    embedder = SentenceTransformer(model_name)

    print("[INFO] Generating embeddings...")

    embeddings = embedder.encode(
        list(texts),
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=False,
    )

    print(
        f"[INFO] Embedding matrix shape: {embeddings.shape}"
    )

    return embeddings


def train_classifier(X_train, y_train):
    """Train the baseline multiclass Logistic Regression classifier."""

    print("\n[INFO] Training Logistic Regression classifier...")

    classifier = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        random_state=42,
        solver="lbfgs",
    )

    classifier.fit(X_train, y_train)

    print("[SUCCESS] Classifier training completed.")

    return classifier


def evaluate_classifier(classifier, X_test, y_test) -> None:
    """Print baseline evaluation metrics."""

    predictions = classifier.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print("\n[INFO] Baseline evaluation")
    print(f"[INFO] Accuracy: {accuracy:.4f}")

    print("\n[INFO] Classification report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=EXPECTED_CLASSES,
            zero_division=0,
        )
    )


def save_artifacts(classifier) -> None:
    """Save the classifier and label mapping used by ModelManager."""

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model": classifier,
        "classes": list(classifier.classes_),
        "embedding_model": (
            "sentence-transformers/"
            "paraphrase-multilingual-MiniLM-L12-v2"
        ),
        "model_type": "logistic_regression",
        "random_state": 42,
    }

    joblib.dump(
        artifact,
        CLASSIFIER_PATH,
        compress=3,
    )

    label_to_id = {
        label: index
        for index, label in enumerate(EXPECTED_CLASSES)
    }

    id_to_label = {
        str(index): label
        for index, label in enumerate(EXPECTED_CLASSES)
    }

    mapping = {
        "classes": EXPECTED_CLASSES,
        "label_to_id": label_to_id,
        "id_to_label": id_to_label,
    }

    with open(MAPPING_PATH, "w", encoding="utf-8") as f:
        json.dump(
            mapping,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("\n[SUCCESS] Saved classifier:")
    print(f"[SUCCESS] {CLASSIFIER_PATH}")

    print("[SUCCESS] Saved label mapping:")
    print(f"[SUCCESS] {MAPPING_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Train the SentryMesh baseline classifier."
    )

    parser.add_argument(
        "--dataset",
        type=str,
        default=str(DEFAULT_DATASET),
        help=(
            "Path to the processed multiclass CSV dataset."
        ),
    )

    args = parser.parse_args()

    dataset_path = Path(args.dataset)

    print("=" * 70)
    print("SentryMesh Baseline Classifier Training")
    print("=" * 70)

    print(f"\n[INFO] Project root: {BASE_DIR}")
    print(f"[INFO] Dataset: {dataset_path}")

    try:
        df = load_dataset(dataset_path)
        validate_labels(df)
        print_dataset_summary(df)

        # Stratified splitting preserves the class distribution between
        # training and validation/test partitions.
        X_train_text, X_test_text, y_train, y_test = train_test_split(
            df["text"],
            df["label"],
            test_size=0.20,
            random_state=42,
            stratify=df["label"],
        )

        print("\n[INFO] Split:")
        print(f"[INFO] Training records: {len(X_train_text)}")
        print(f"[INFO] Test records: {len(X_test_text)}")

        # Save the exact test partition used during this training run.
        # This ensures evaluate_model.py evaluates the same held-out
        # examples that were used above.
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

        test_df = pd.DataFrame(
            {
                "text": X_test_text.values,
                "label": y_test.values,
            }
        )

        test_df.to_csv(
            TEST_DATASET_PATH,
            index=False,
            encoding="utf-8",
        )

        print("[SUCCESS] Saved exact held-out test partition:")
        print(f"[SUCCESS] {TEST_DATASET_PATH}")

        X_train = create_embeddings(X_train_text)
        X_test = create_embeddings(X_test_text)

        classifier = train_classifier(
            X_train,
            y_train,
        )

        evaluate_classifier(
            classifier,
            X_test,
            y_test,
        )

        save_artifacts(classifier)

        print("\n" + "=" * 70)
        print("[SUCCESS] SentryMesh baseline training completed.")
        print("=" * 70)

        return 0

    except Exception as exc:
        print(
            f"\n[ERROR] Training failed: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())