"""
Prepare the real public phishing/spam email dataset for SentryMesh.

Source:
K2509118/seven-phishing-email-datasets_pub
https://huggingface.co/datasets/K2509118/seven-phishing-email-datasets_pub

Important:
- Keeps the original binary label.
- Does NOT relabel every spam email as phishing.
- Preserves the original dataset/corpus name.
- Combines subject + body into a single analysis text.
- Removes empty and duplicate records.
"""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR = PROJECT_ROOT / "data" / "raw" / "phishing_email_hf"
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "sentrymesh_real_email.csv"


REQUIRED_COLUMNS = {
    "text",
    "subject",
    "label",
    "sender",
    "receiver",
    "date",
    "urls",
    "dataset_name",
}


def clean_text(value) -> str:
    """Normalize whitespace without changing the actual message meaning."""
    if pd.isna(value):
        return ""

    text = str(value)
    text = " ".join(text.split())
    return text.strip()


def combine_subject_and_body(subject, body) -> str:
    """Create the text that MessageGuard will analyze."""
    subject = clean_text(subject)
    body = clean_text(body)

    if subject and body:
        return f"Subject: {subject}\n\n{body}"

    return subject or body


def prepare_split(path: Path) -> pd.DataFrame:
    """Load and normalize one parquet split."""
    df = pd.read_parquet(path)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns in {path.name}: {sorted(missing)}"
        )

    result = pd.DataFrame()

    result["text"] = [
        combine_subject_and_body(subject, body)
        for subject, body in zip(df["subject"], df["text"])
    ]

    result["original_label"] = df["label"].astype(str)

    result["label"] = df["label"].map(
        {
            0: "legitimate",
            1: "spam_or_phishing",
            "0": "legitimate",
            "1": "spam_or_phishing",
        }
    )

    result["sender"] = df["sender"].fillna("").astype(str).map(clean_text)
    result["receiver"] = df["receiver"].fillna("").astype(str).map(clean_text)
    result["date"] = df["date"].fillna("").astype(str)
    result["urls"] = df["urls"].astype("string").fillna("").astype(str)
    result["source_dataset"] = (
        df["dataset_name"].fillna("unknown").astype(str).map(clean_text)
    )

    result["channel"] = "email"
    result["language"] = "en"
    result["source"] = "real_public_email_corpus"

    return result


def main() -> None:
    train_path = INPUT_DIR / "train.parquet"
    test_path = INPUT_DIR / "test.parquet"

    if not train_path.exists():
        raise FileNotFoundError(
            f"Training dataset not found:\n{train_path}"
        )

    if not test_path.exists():
        raise FileNotFoundError(
            f"Test dataset not found:\n{test_path}"
        )

    print("Loading real email dataset...")

    train_df = prepare_split(train_path)
    test_df = prepare_split(test_path)

    train_df["split"] = "train"
    test_df["split"] = "test"

    combined = pd.concat(
        [train_df, test_df],
        ignore_index=True,
    )

    before = len(combined)

    combined["text"] = combined["text"].map(clean_text)

    combined = combined[combined["text"].str.len() >= 10]

    combined = combined.drop_duplicates(
        subset=["text"],
        keep="first",
    )

    combined = combined.reset_index(drop=True)

    after = len(combined)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    combined.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    print()
    print("Real email dataset prepared successfully.")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Rows before cleaning: {before}")
    print(f"Rows after cleaning:  {after}")
    print()
    print("Labels:")
    print(combined["label"].value_counts())
    print()
    print("Source corpora:")
    print(combined["source_dataset"].value_counts())
    print()
    print("Splits:")
    print(combined["split"].value_counts())


if __name__ == "__main__":
    main()