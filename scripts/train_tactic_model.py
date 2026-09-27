"""Trainer for SentryMesh Multi-Label Cognitive Tactic Model.

Data Source:
  data/raw/sentrymesh_tactics.csv

Tactics Evaluated:
  - authority_impersonation
  - urgency
  - fear_or_threat
  - secrecy
  - isolation
  - payment_request
  - otp_request
  - credential_request
  - remote_access_request
  - screen_share_request
  - upi_collect_request

Artifacts Produced:
  - models/tactic_model.joblib
  - models/tactic_mapping.json

Usage:
  Tactics are NOT used as manually assigned fraud scores.
  They are learned multi-label evidence vectors that empower explainability:
  answering *why* a message is manipulative without black-box assumptions.
"""

import os
import csv
import json

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
MODELS_DIR = os.path.join(BASE_DIR, "models")
TACTICS_CSV = os.path.join(RAW_DIR, "sentrymesh_tactics.csv")

TACTIC_NAMES = [
    "authority_impersonation",
    "urgency",
    "fear_or_threat",
    "secrecy",
    "isolation",
    "payment_request",
    "otp_request",
    "credential_request",
    "remote_access_request",
    "screen_share_request",
    "upi_collect_request",
]


def train_tactic_model():
    """Train the multi-label tactic predictor and export artifacts."""

    os.makedirs(MODELS_DIR, exist_ok=True)

    print("[INFO] Training SentryMesh Multi-Label Cognitive Tactic Model...")

    if not os.path.exists(TACTICS_CSV):
        raise FileNotFoundError(
            f"Tactics dataset not found at {TACTICS_CSV}. "
            "Run create_synthetic_data.py first."
        )

    texts = []
    labels = []

    with open(TACTICS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            text = str(row.get("text", "")).strip()

            if not text:
                continue

            texts.append(text)

            vector = [
                int(row.get(tactic, 0))
                for tactic in TACTIC_NAMES
            ]

            labels.append(vector)

    if not texts:
        raise ValueError("No usable tactic training samples were found.")

    print(
        f"[INFO] Loaded {len(texts)} tactic-annotated training samples "
        f"across {len(TACTIC_NAMES)} tactics."
    )

    # Save tactic mapping.
    mapping_path = os.path.join(
        MODELS_DIR,
        "tactic_mapping.json",
    )

    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "tactics": TACTIC_NAMES,
                "description": (
                    "Learned multi-label manipulation indicators "
                    "for explanation synthesis"
                ),
            },
            f,
            indent=2,
        )

    print(
        f"[SUCCESS] Tactic mapping saved to: {mapping_path}"
    )

    try:
        from sentence_transformers import SentenceTransformer
        from sklearn.multioutput import MultiOutputClassifier
        from sklearn.linear_model import LogisticRegression
        import joblib
        import numpy as np

        model_name = (
            "sentence-transformers/"
            "paraphrase-multilingual-MiniLM-L12-v2"
        )

        print(f"[INFO] Encoding text using {model_name}...")

        embedder = SentenceTransformer(model_name)

        X_emb = embedder.encode(
            texts,
            show_progress_bar=True,
            batch_size=32,
            convert_to_numpy=True,
        )

        y_mat = np.array(labels)

        print(
            "[INFO] Fitting "
            "MultiOutputClassifier("
            "LogisticRegression(class_weight='balanced'))..."
        )

        base_lr = LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=42,
        )

        multi_target = MultiOutputClassifier(base_lr)

        multi_target.fit(
            X_emb,
            y_mat,
        )

        model_path = os.path.join(
            MODELS_DIR,
            "tactic_model.joblib",
        )

        joblib.dump(
            {
                "model": multi_target,
                "tactics": TACTIC_NAMES,
                "embedding_model": model_name,
                "model_type": "multi_output_logistic_regression",
                "random_state": 42,
            },
            model_path,
        )

        print(
            f"[SUCCESS] Saved multi-label tactic model to: "
            f"{model_path}"
        )

    except ImportError as exc:
        raise RuntimeError(
            "Required ML dependencies are not installed. "
            "Install sentence-transformers, scikit-learn, numpy, "
            "and joblib before training the tactic model."
        ) from exc

    return TACTIC_NAMES


if __name__ == "__main__":
    train_tactic_model()