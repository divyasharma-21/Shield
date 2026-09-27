from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = BASE_DIR / "data" / "raw"

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "sentrymesh_binary_v4.csv"
)

CALL_SCAMS_PATH = (
    RAW_DIR
    / "sentrymesh_call_scams.csv"
)

UPI_QR_SCAMS_PATH = (
    RAW_DIR
    / "sentrymesh_upi_qr_scams.csv"
)

HIGH_HARM_PATH = (
    RAW_DIR
    / "sentrymesh_high_harm_fraud_v2.csv"
)

LEGITIMATE_PATH = (
    RAW_DIR
    / "sentrymesh_legitimate_indian.csv"
)

MULTILINGUAL_REMOTE_ACCESS_PATH = (
    RAW_DIR
    / "sentrymesh_multilingual_remote_access_v4.csv"
)

UCI_PATH = (
    RAW_DIR
    / "uci_sms_processed.csv"
)

RANDOM_STATE = 42

UCI_LEGITIMATE_SAMPLES = 250
UCI_SUSPICIOUS_SAMPLES = 70


def load_required_dataset(path):
    if not path.exists():
        raise FileNotFoundError(
            f"Required dataset was not found:\n{path}"
        )

    dataframe = pd.read_csv(path)

    required_columns = {
        "text",
        "label",
        "channel",
        "language",
        "source"
    }

    missing_columns = required_columns - set(
        dataframe.columns
    )

    if missing_columns:
        raise ValueError(
            f"{path.name} is missing columns: "
            f"{sorted(missing_columns)}"
        )

    dataframe = dataframe[
        [
            "text",
            "label",
            "channel",
            "language",
            "source"
        ]
    ].copy()

    dataframe = dataframe.dropna(
        subset=["text", "label"]
    )

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
    ].copy()

    return dataframe


def make_binary_labels(dataframe):
    dataframe = dataframe.copy()

    dataframe["label"] = dataframe["label"].apply(
        lambda value: (
            "legitimate"
            if str(value).strip().lower()
            == "legitimate"
            else "suspicious"
        )
    )

    return dataframe


def sample_uci_data():
    uci_dataframe = load_required_dataset(
        UCI_PATH
    )

    uci_legitimate = uci_dataframe[
        uci_dataframe["label"] == "legitimate"
    ].sample(
        n=UCI_LEGITIMATE_SAMPLES,
        random_state=RANDOM_STATE
    )

    uci_suspicious = uci_dataframe[
        uci_dataframe["label"] == "other_suspicious"
    ].sample(
        n=UCI_SUSPICIOUS_SAMPLES,
        random_state=RANDOM_STATE
    )

    return (
        make_binary_labels(uci_legitimate),
        make_binary_labels(uci_suspicious)
    )


def main():
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\nLoading SentryMesh fraud datasets...")

    call_scams = make_binary_labels(
        load_required_dataset(CALL_SCAMS_PATH)
    )

    upi_qr_scams = make_binary_labels(
        load_required_dataset(UPI_QR_SCAMS_PATH)
    )

    high_harm = make_binary_labels(
        load_required_dataset(HIGH_HARM_PATH)
    )

    legitimate_indian = make_binary_labels(
        load_required_dataset(LEGITIMATE_PATH)
    )

    multilingual_remote_access = make_binary_labels(
        load_required_dataset(
            MULTILINGUAL_REMOTE_ACCESS_PATH
        )
    )

    print("Loading controlled UCI SMS sample...")

    uci_legitimate, uci_suspicious = (
        sample_uci_data()
    )

    dataframe = pd.concat(
        [
            call_scams,
            upi_qr_scams,
            high_harm,
            legitimate_indian,
            multilingual_remote_access,
            uci_legitimate,
            uci_suspicious
        ],
        ignore_index=True
    )

    duplicate_count = int(
        dataframe.duplicated(
            subset=["text"]
        ).sum()
    )

    dataframe = dataframe.drop_duplicates(
        subset=["text"]
    ).copy()

    dataframe = dataframe.sample(
        frac=1,
        random_state=RANDOM_STATE
    ).reset_index(
        drop=True
    )

    valid_labels = {
        "legitimate",
        "suspicious"
    }

    found_labels = set(
        dataframe["label"].unique()
    )

    unexpected_labels = found_labels - valid_labels

    if unexpected_labels:
        raise ValueError(
            "Unexpected binary labels found: "
            f"{sorted(unexpected_labels)}"
        )

    dataframe.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nBinary V4 dataset created successfully.")
    print("Saved to:")
    print(OUTPUT_PATH)

    print("\nDuplicate texts removed:")
    print(duplicate_count)

    print("\nDataset shape:")
    print(dataframe.shape)

    print("\nBinary class distribution:")
    print(
        dataframe["label"].value_counts()
    )

    print("\nDistribution by language and label:")
    print(
        pd.crosstab(
            dataframe["language"],
            dataframe["label"]
        )
    )

    print("\nDistribution by source and label:")
    print(
        pd.crosstab(
            dataframe["source"],
            dataframe["label"]
        )
    )


if __name__ == "__main__":
    main()