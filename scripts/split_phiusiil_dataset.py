"""
Create a domain-aware train/test split for the PhiUSIIL WebGuard dataset.

The split is performed at the Domain level so URLs from the same domain
do not normally appear in both training and testing data.
"""

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = PROJECT_ROOT / "data" / "raw" / "sentrymesh_phiusiil.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"

TRAIN_FILE = OUTPUT_DIR / "webguard_train.csv"
TEST_FILE = OUTPUT_DIR / "webguard_test.csv"


def main() -> None:
    print("Loading PhiUSIIL dataset...")

    df = pd.read_csv(INPUT_FILE)

    required_columns = {"URL", "Domain", "label"}

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    # One row per domain with its dominant label.
    domain_labels = (
        df.groupby("Domain")["label"]
        .agg(lambda values: values.mode().iloc[0])
        .reset_index()
    )

    train_domains, test_domains = train_test_split(
        domain_labels,
        test_size=0.20,
        random_state=42,
        stratify=domain_labels["label"],
    )

    train_domain_set = set(train_domains["Domain"])
    test_domain_set = set(test_domains["Domain"])

    train_df = df[df["Domain"].isin(train_domain_set)].copy()
    test_df = df[df["Domain"].isin(test_domain_set)].copy()

    # Verify there is no domain overlap.
    overlap = train_domain_set & test_domain_set

    if overlap:
        raise RuntimeError(
            f"Domain leakage detected: {len(overlap)} overlapping domains."
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    train_df.to_csv(
        TRAIN_FILE,
        index=False,
        encoding="utf-8",
    )

    test_df.to_csv(
        TEST_FILE,
        index=False,
        encoding="utf-8",
    )

    print()
    print("Domain-aware split created successfully.")
    print(f"Total rows: {len(df)}")
    print(f"Training rows: {len(train_df)}")
    print(f"Testing rows: {len(test_df)}")
    print()
    print(f"Training domains: {len(train_domain_set)}")
    print(f"Testing domains: {len(test_domain_set)}")
    print(f"Domain overlap: {len(overlap)}")
    print()
    print("Training labels:")
    print(train_df["label"].value_counts())
    print()
    print("Testing labels:")
    print(test_df["label"].value_counts())


if __name__ == "__main__":
    main()