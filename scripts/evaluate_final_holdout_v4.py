from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)


BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "sentrymesh_binary_tfidf_v4.joblib"
)

MODEL_METRICS_PATH = (
    BASE_DIR
    / "reports"
    / "sentrymesh_binary_tfidf_v4_metrics.json"
)

TRAINING_DATA_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "sentrymesh_binary_v4.csv"
)

FINAL_HOLDOUT_PATH = (
    BASE_DIR
    / "data"
    / "final_holdout"
    / "sentrymesh_final_holdout_v1.csv"
)

RESULTS_PATH = (
    BASE_DIR
    / "reports"
    / "sentrymesh_final_holdout_v1_v4_results.csv"
)

METRICS_PATH = (
    BASE_DIR
    / "reports"
    / "sentrymesh_final_holdout_v1_v4_metrics.json"
)

VALID_LABELS = {
    "legitimate",
    "authority_impersonation_scam",
    "remote_access_scam",
    "UPI_QR_scam",
    "payment_or_credential_scam",
    "fake_payment_scam"
}

REQUIRED_COLUMNS = {
    "id",
    "text",
    "label",
    "channel",
    "language",
    "source",
    "source_reference",
    "reviewer",
    "holdout_lock_date"
}


def normalize_text(value):
    return " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )


def load_model_and_threshold():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"V4 model was not found:\n{MODEL_PATH}"
        )

    if not MODEL_METRICS_PATH.exists():
        raise FileNotFoundError(
            f"V4 model metrics were not found:\n"
            f"{MODEL_METRICS_PATH}"
        )

    model = joblib.load(MODEL_PATH)

    with open(
        MODEL_METRICS_PATH,
        "r",
        encoding="utf-8"
    ) as metrics_file:
        model_metrics = json.load(metrics_file)

    threshold = model_metrics.get(
        "selected_suspicious_threshold"
    )

    if threshold is None:
        raise ValueError(
            "V4 metrics do not contain "
            "selected_suspicious_threshold."
        )

    return model, float(threshold)


def load_final_holdout():
    if not FINAL_HOLDOUT_PATH.exists():
        raise FileNotFoundError(
            f"Final holdout CSV was not found:\n"
            f"{FINAL_HOLDOUT_PATH}"
        )

    dataframe = pd.read_csv(FINAL_HOLDOUT_PATH)

    missing_columns = REQUIRED_COLUMNS - set(
        dataframe.columns
    )

    if missing_columns:
        raise ValueError(
            "Final holdout CSV is missing required "
            f"columns: {sorted(missing_columns)}"
        )

    dataframe = dataframe.copy()

    for column in REQUIRED_COLUMNS:
        dataframe[column] = (
            dataframe[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    empty_required_values = dataframe[
        list(REQUIRED_COLUMNS)
    ].eq("").any(axis=1)

    if empty_required_values.any():
        invalid_ids = dataframe.loc[
            empty_required_values,
            "id"
        ].tolist()

        raise ValueError(
            "Final holdout contains empty required "
            f"values for IDs: {invalid_ids}"
        )

    if dataframe["id"].duplicated().any():
        duplicate_ids = dataframe.loc[
            dataframe["id"].duplicated(
                keep=False
            ),
            "id"
        ].tolist()

        raise ValueError(
            "Final holdout contains duplicate IDs: "
            f"{duplicate_ids}"
        )

    if dataframe["text"].str.len().lt(10).any():
        short_ids = dataframe.loc[
            dataframe["text"].str.len().lt(10),
            "id"
        ].tolist()

        raise ValueError(
            "Final holdout contains text shorter than "
            f"10 characters for IDs: {short_ids}"
        )

    unexpected_labels = set(
        dataframe["label"].unique()
    ) - VALID_LABELS

    if unexpected_labels:
        raise ValueError(
            "Final holdout contains unexpected labels: "
            f"{sorted(unexpected_labels)}"
        )

    dataframe["text_key"] = dataframe["text"].apply(
        normalize_text
    )

    if dataframe["text_key"].duplicated().any():
        duplicate_ids = dataframe.loc[
            dataframe["text_key"].duplicated(
                keep=False
            ),
            "id"
        ].tolist()

        raise ValueError(
            "Final holdout contains duplicate or "
            "near-identical normalized text for IDs: "
            f"{duplicate_ids}"
        )

    dataframe["actual_binary_label"] = (
        dataframe["label"].apply(
            lambda value: (
                "legitimate"
                if value == "legitimate"
                else "suspicious"
            )
        )
    )

    return dataframe


def check_training_leakage(holdout_dataframe):
    if not TRAINING_DATA_PATH.exists():
        raise FileNotFoundError(
            f"V4 training dataset was not found:\n"
            f"{TRAINING_DATA_PATH}"
        )

    training_dataframe = pd.read_csv(
        TRAINING_DATA_PATH
    )

    if "text" not in training_dataframe.columns:
        raise ValueError(
            "V4 training dataset does not contain "
            "a text column."
        )

    training_text_keys = set(
        training_dataframe["text"]
        .fillna("")
        .apply(normalize_text)
    )

    leakage_rows = holdout_dataframe[
        holdout_dataframe["text_key"].isin(
            training_text_keys
        )
    ].copy()

    if not leakage_rows.empty:
        leaked_ids = leakage_rows["id"].tolist()

        raise ValueError(
            "\nDATA LEAKAGE DETECTED.\n"
            "The following final-holdout IDs exactly "
            "match normalized V4 training text:\n"
            f"{leaked_ids}\n\n"
            "Do not run final evaluation until the "
            "holdout is replaced with unseen examples."
        )

    return int(len(leakage_rows))


def get_suspicious_probabilities(model, texts):
    probabilities = model.predict_proba(texts)

    suspicious_index = list(
        model.classes_
    ).index("suspicious")

    return probabilities[:, suspicious_index]


def get_predicted_label(probability, threshold):
    if probability >= threshold:
        return "suspicious"

    return "legitimate"


def get_safety_level(probability, threshold):
    if probability >= 0.80:
        return "high_risk"

    if probability >= threshold:
        return "suspicious_needs_verification"

    if probability >= threshold - 0.10:
        return "uncertain_needs_verification"

    return "no_strong_risk_signal"


def main():
    print("\nLoading frozen SentryMesh V4 model...")

    model, threshold = load_model_and_threshold()

    print("Selected suspicious threshold:", threshold)

    print("\nLoading locked final holdout dataset...")

    dataframe = load_final_holdout()

    print("Final holdout examples:", len(dataframe))

    print("\nChecking for V4 training-data leakage...")

    leakage_count = check_training_leakage(dataframe)

    print("Leakage check passed.")
    print("Exact normalized training-text matches:", leakage_count)

    print("\nFinal holdout category distribution:")

    print(
        dataframe["label"].value_counts()
    )

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
            lambda value: get_predicted_label(
                value,
                threshold
            )
        )
    )

    dataframe["safety_level"] = dataframe[
        "suspicious_probability"
    ].apply(
        lambda value: get_safety_level(
            value,
            threshold
        )
    )

    y_true = dataframe["actual_binary_label"]

    y_pred = dataframe["predicted_binary_label"]

    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    weighted_precision, weighted_recall, weighted_f1, _ = (
        precision_recall_fscore_support(
            y_true,
            y_pred,
            average="weighted",
            zero_division=0
        )
    )

    print("\nFinal Holdout Classification Report:\n")

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

    print("\nFinal evaluation summary:")

    print("Total examples:", len(dataframe))

    print(
        "Correct predictions:",
        int(dataframe["correct"].sum())
    )

    print(
        "Wrong predictions:",
        int((~dataframe["correct"]).sum())
    )

    print("Accuracy:", round(accuracy, 4))

    print(
        "Weighted precision:",
        round(weighted_precision, 4)
    )

    print(
        "Weighted recall:",
        round(weighted_recall, 4)
    )

    print(
        "Weighted F1 score:",
        round(weighted_f1, 4)
    )

    print("False negatives:", len(false_negatives))

    print("False positives:", len(false_positives))

    print("\nSafety-level distribution:")

    print(
        dataframe["safety_level"].value_counts()
    )

    print("\nResults by original category:")

    print(
        pd.crosstab(
            dataframe["label"],
            dataframe["predicted_binary_label"]
        )
    )

    output_columns = [
        "id",
        "text",
        "label",
        "actual_binary_label",
        "predicted_binary_label",
        "suspicious_probability",
        "selected_threshold",
        "safety_level",
        "channel",
        "language",
        "source",
        "source_reference",
        "reviewer",
        "holdout_lock_date",
        "correct"
    ]

    if false_negatives.empty:
        print("\nFalse negatives: None")
    else:
        print(
            "\nFalse negatives "
            "(scams predicted as legitimate):"
        )

        print(
            false_negatives[
                output_columns
            ].to_string(
                index=False
            )
        )

    if false_positives.empty:
        print("\nFalse positives: None")
    else:
        print(
            "\nFalse positives "
            "(legitimate messages predicted as suspicious):"
        )

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

    dataframe[
        output_columns
    ].to_csv(
        RESULTS_PATH,
        index=False
    )

    final_metrics = {
        "evaluation_name": (
            "sentrymesh_final_holdout_v1_v4"
        ),
        "model_path": str(MODEL_PATH),
        "training_data_path": str(
            TRAINING_DATA_PATH
        ),
        "final_holdout_path": str(
            FINAL_HOLDOUT_PATH
        ),
        "total_examples": int(len(dataframe)),
        "selected_suspicious_threshold": threshold,
        "exact_training_text_matches": leakage_count,
        "accuracy": float(accuracy),
        "weighted_precision": float(
            weighted_precision
        ),
        "weighted_recall": float(
            weighted_recall
        ),
        "weighted_f1": float(weighted_f1),
        "false_negatives": int(
            len(false_negatives)
        ),
        "false_positives": int(
            len(false_positives)
        ),
        "category_distribution": {
            key: int(value)
            for key, value in dataframe[
                "label"
            ].value_counts().to_dict().items()
        },
        "safety_level_distribution": {
            key: int(value)
            for key, value in dataframe[
                "safety_level"
            ].value_counts().to_dict().items()
        },
        "evaluation_integrity_note": (
            "The V4 model and 0.40 threshold were frozen "
            "before this final-holdout evaluation. "
            "No exact normalized text overlap with the "
            "V4 processed training dataset was detected."
        )
    }

    with open(
        METRICS_PATH,
        "w",
        encoding="utf-8"
    ) as metrics_file:
        json.dump(
            final_metrics,
            metrics_file,
            indent=2,
            ensure_ascii=False
        )

    print("\nSaved final-holdout results to:")

    print(RESULTS_PATH)

    print("\nSaved final-holdout metrics to:")

    print(METRICS_PATH)

    print(
        "\nImportant: Do not change V4 training data, "
        "threshold, or model settings after viewing "
        "this final result. If a new model is trained, "
        "create a new final holdout."
    )


if __name__ == "__main__":
    main()