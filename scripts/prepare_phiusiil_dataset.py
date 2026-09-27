"""
Prepare the real UCI PhiUSIIL Phishing URL dataset for SentryMesh WebGuard.

Source:
UCI Machine Learning Repository
PhiUSIIL Phishing URL (Website) Dataset
https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset

The original 54 features are preserved.
The original UCI label is preserved as original_label.
"""

from pathlib import Path

import pandas as pd
from ucimlrepo import fetch_ucirepo


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "sentrymesh_phiusiil.csv"


def main() -> None:
    print("Loading UCI PhiUSIIL dataset...")

    dataset = fetch_ucirepo(id=967)

    features = dataset.data.features.copy()
    targets = dataset.data.targets.copy()

    print(f"Rows loaded: {len(features)}")
    print(f"Feature columns: {len(features.columns)}")

    if "label" not in targets.columns:
        raise ValueError("Expected 'label' target column was not found.")

    result = features.copy()

    result["original_label"] = targets["label"].values

    # UCI PhiUSIIL uses:
    # 1 = phishing
    # 0 = legitimate
    result["label"] = result["original_label"].map(
        {
            0: "legitimate",
            1: "phishing",
            "0": "legitimate",
            "1": "phishing",
        }
    )

    if result["label"].isna().any():
        unknown = result.loc[
            result["label"].isna(),
            "original_label"
        ].unique()

        raise ValueError(
            f"Unexpected label values found: {unknown}"
        )

    result["source_dataset"] = "UCI_PhiUSIIL"
    result["source"] = "real_public_uci"
    result["channel"] = "web"
    result["language"] = "unknown"

    before = len(result)

    result = result.drop_duplicates(
        subset=["URL"],
        keep="first",
    )

    result = result.reset_index(drop=True)

    after = len(result)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8",
    )

    print()
    print("PhiUSIIL dataset prepared successfully.")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Rows before deduplication: {before}")
    print(f"Rows after deduplication:  {after}")
    print()
    print("Labels:")
    print(result["label"].value_counts())
    print()
    print("Columns:")
    print(result.columns.tolist())


if __name__ == "__main__":
    main()