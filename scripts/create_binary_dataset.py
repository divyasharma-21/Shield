from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "sentrymesh_multiclass_v1.csv"
)

OUTPUT_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "sentrymesh_binary_v1.csv"
)


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input file not found:\n{INPUT_PATH}"
        )

    dataframe = pd.read_csv(INPUT_PATH)

    required_columns = {
        "text",
        "label"
    }

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    dataframe = dataframe.dropna(
        subset=["text", "label"]
    ).copy()

    dataframe["binary_label"] = dataframe["label"].apply(
        lambda value: (
            "legitimate"
            if str(value).strip().lower() == "legitimate"
            else "suspicious"
        )
    )

    output_columns = [
        "text",
        "binary_label"
    ]

    for optional_column in [
        "normalized_text",
        "channel",
        "language",
        "source"
    ]:
        if optional_column in dataframe.columns:
            output_columns.append(optional_column)

    binary_dataframe = dataframe[
        output_columns
    ].rename(
        columns={
            "binary_label": "label"
        }
    )

    binary_dataframe.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nBinary dataset created successfully.")
    print("Saved to:")
    print(OUTPUT_PATH)

    print("\nBinary class distribution:")
    print(
        binary_dataframe["label"].value_counts()
    )


if __name__ == "__main__":
    main()