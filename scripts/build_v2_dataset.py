from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

CUSTOM_DATASET_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "sentrymesh_multiclass_v1.csv"
)

UCI_DATASET_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "uci_sms_processed.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "sentrymesh_multiclass_v2.csv"
)

RANDOM_SEED = 42

UCI_LEGITIMATE_SAMPLE_SIZE = 300
UCI_SUSPICIOUS_SAMPLE_SIZE = 300


def require_columns(dataframe, required_columns, dataset_name):
    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing columns: "
            f"{sorted(missing_columns)}"
        )


def clean_dataframe(dataframe):
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

    return dataframe


def main():
    if not CUSTOM_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Custom SentryMesh dataset not found:\n"
            f"{CUSTOM_DATASET_PATH}"
        )

    if not UCI_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"UCI SMS dataset not found:\n"
            f"{UCI_DATASET_PATH}"
        )

    print("\nLoading SentryMesh custom dataset...")

    custom_dataframe = pd.read_csv(
        CUSTOM_DATASET_PATH
    )

    require_columns(
        custom_dataframe,
        {"text", "label"},
        "Custom SentryMesh dataset"
    )

    custom_dataframe = clean_dataframe(
        custom_dataframe
    )

    print(
        "Custom records:",
        len(custom_dataframe)
    )

    print("\nLoading real UCI SMS dataset...")

    uci_dataframe = pd.read_csv(
        UCI_DATASET_PATH
    )

    require_columns(
        uci_dataframe,
        {"text", "label"},
        "UCI SMS dataset"
    )

    uci_dataframe = clean_dataframe(
        uci_dataframe
    )

    if "channel" not in uci_dataframe.columns:
        uci_dataframe["channel"] = "sms"

    if "language" not in uci_dataframe.columns:
        uci_dataframe["language"] = "en"

    if "source" not in uci_dataframe.columns:
        uci_dataframe["source"] = "uci_sms"

    uci_legitimate = uci_dataframe[
        uci_dataframe["label"] == "legitimate"
    ]

    uci_suspicious = uci_dataframe[
        uci_dataframe["label"] == "other_suspicious"
    ]

    if len(uci_legitimate) < UCI_LEGITIMATE_SAMPLE_SIZE:
        raise ValueError(
            "Not enough legitimate UCI records "
            "for requested sample size."
        )

    if len(uci_suspicious) < UCI_SUSPICIOUS_SAMPLE_SIZE:
        raise ValueError(
            "Not enough suspicious UCI records "
            "for requested sample size."
        )

    sampled_uci_legitimate = uci_legitimate.sample(
        n=UCI_LEGITIMATE_SAMPLE_SIZE,
        random_state=RANDOM_SEED
    )

    sampled_uci_suspicious = uci_suspicious.sample(
        n=UCI_SUSPICIOUS_SAMPLE_SIZE,
        random_state=RANDOM_SEED
    )

    sampled_uci = pd.concat(
        [
            sampled_uci_legitimate,
            sampled_uci_suspicious
        ],
        ignore_index=True
    )

    required_output_columns = [
        "text",
        "label",
        "channel",
        "language",
        "source"
    ]

    for column in required_output_columns:
        if column not in custom_dataframe.columns:
            custom_dataframe[column] = "unknown"

    custom_dataframe = custom_dataframe[
        required_output_columns
    ]

    sampled_uci = sampled_uci[
        required_output_columns
    ]

    combined_dataframe = pd.concat(
        [
            custom_dataframe,
            sampled_uci
        ],
        ignore_index=True
    )

    combined_dataframe = clean_dataframe(
        combined_dataframe
    )

    combined_dataframe = combined_dataframe.sample(
        frac=1,
        random_state=RANDOM_SEED
    ).reset_index(
        drop=True
    )

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    combined_dataframe.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nVersion 2 dataset built successfully.")

    print("\nSaved to:")
    print(OUTPUT_PATH)

    print("\nFinal dataset shape:")
    print(combined_dataframe.shape)

    print("\nClass distribution:")
    print(
        combined_dataframe["label"].value_counts()
    )

    print("\nSource distribution:")
    print(
        combined_dataframe["source"].value_counts()
    )

    print("\nLanguage distribution:")
    print(
        combined_dataframe["language"].value_counts()
    )


if __name__ == "__main__":
    main()