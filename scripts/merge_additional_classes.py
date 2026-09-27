import os
import sys
import pandas as pd

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

sys.path.insert(0, PROJECT_ROOT)

from app.extractor import normalize_input_text


PROCESSED_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "sentrymesh_multiclass_v1.csv",
)

ADDITIONAL_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "raw",
    "sentrymesh_additional_classes.csv",
)


EXPECTED_COLUMNS = [
    "text",
    "normalized_text",
    "label",
    "channel",
    "language",
    "source",
]


REQUIRED_CLASSES = {
    "legitimate",
    "phishing",
    "payment_or_credential_scam",
    "authority_impersonation_scam",
    "remote_access_scam",
    "UPI_QR_scam",
    "fake_payment_scam",
    "other_suspicious",
}


def main():
    print("=" * 70)
    print("SentryMesh Dataset Merge")
    print("=" * 70)

    if not os.path.exists(PROCESSED_PATH):
        raise FileNotFoundError(
            f"Processed dataset not found: {PROCESSED_PATH}"
        )

    if not os.path.exists(ADDITIONAL_PATH):
        raise FileNotFoundError(
            f"Additional classes dataset not found: {ADDITIONAL_PATH}"
        )

    base_df = pd.read_csv(PROCESSED_PATH)
    additional_df = pd.read_csv(ADDITIONAL_PATH)

    print(f"\n[INFO] Existing rows: {len(base_df)}")
    print(f"[INFO] Additional rows: {len(additional_df)}")

    required_additional_columns = {
        "text",
        "label",
        "channel",
        "language",
        "source",
    }

    missing = required_additional_columns - set(additional_df.columns)

    if missing:
        raise ValueError(
            f"Additional dataset is missing columns: {sorted(missing)}"
        )

    if not set(EXPECTED_COLUMNS).issuperset(base_df.columns):
        raise ValueError(
            f"Unexpected columns in processed dataset: {list(base_df.columns)}"
        )

    # Generate normalized text for the new examples
    # using the same normalization function as the main pipeline.
    additional_df["normalized_text"] = additional_df["text"].apply(
        normalize_input_text
    )

    additional_df = additional_df[EXPECTED_COLUMNS]

    # Remove additional messages that already exist in the
    # processed dataset.
    existing_texts = set(
        base_df["text"].astype(str).str.strip()
    )

    before = len(additional_df)

    additional_df = additional_df[
        ~additional_df["text"]
        .astype(str)
        .str.strip()
        .isin(existing_texts)
    ].copy()

    duplicates_removed = before - len(additional_df)

    print(
        f"[INFO] Duplicate additional rows removed: "
        f"{duplicates_removed}"
    )

    # Combine the datasets.
    merged_df = pd.concat(
        [
            base_df[EXPECTED_COLUMNS],
            additional_df,
        ],
        ignore_index=True,
    )

    # Remove exact duplicate text + label combinations.
    merged_df = merged_df.drop_duplicates(
        subset=["text", "label"],
        keep="first",
    ).reset_index(drop=True)

    # Verify that all required classes are present.
    present_classes = set(
        merged_df["label"].dropna().unique()
    )

    missing_classes = REQUIRED_CLASSES - present_classes

    print("\n[INFO] Final class distribution:")
    print(
        merged_df["label"]
        .value_counts()
        .to_string()
    )

    if missing_classes:
        raise ValueError(
            "Dataset is still missing required classes: "
            f"{sorted(missing_classes)}"
        )

    # Save the merged dataset.
    merged_df.to_csv(
        PROCESSED_PATH,
        index=False,
        encoding="utf-8",
    )

    print(f"\n[INFO] Final rows: {len(merged_df)}")

    print(
        f"[SUCCESS] Saved merged dataset to: "
        f"{PROCESSED_PATH}"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\n[ERROR] Merge failed: {exc}")
        raise