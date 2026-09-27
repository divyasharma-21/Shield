"""Automated fetcher and parser for the UCI SMS Spam Collection.

Dataset: SMS Spam Collection
Source: https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip
Format: Tab-separated values: [raw_label, text]
Mapping:
  ham  -> legitimate
  spam -> other_suspicious
Metadata:
  channel = sms
  language = en
  source = uci_sms
"""

import os
import sys
import io
import zipfile
import urllib.request
import pandas as pd

UCI_SMS_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip"
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUTPUT_CSV_PATH = os.path.join(RAW_DATA_DIR, "uci_sms_processed.csv")


def download_and_process_uci_sms(url: str = UCI_SMS_URL, output_path: str = OUTPUT_CSV_PATH) -> pd.DataFrame:
    """Downloads, extracts, maps labels, and saves the UCI SMS Spam Collection."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"[INFO] Fetching UCI SMS Spam dataset from {url}...")

    headers = {"User-Agent": "SentryMeshGuardian-DataFetcher/1.0"}
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            zip_bytes = response.read()
    except Exception as exc:
        print(f"[ERROR] Failed to download UCI SMS zip: {exc}", file=sys.stderr)
        raise

    print("[INFO] Extracting SMSSpamCollection archive...")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zip_ref:
        file_names = zip_ref.namelist()
        target_file = None
        for name in file_names:
            if "SMSSpamCollection" in name and not name.endswith("/"):
                target_file = name
                break

        if not target_file:
            raise FileNotFoundError("SMSSpamCollection not found within the downloaded zip archive.")

        with zip_ref.open(target_file) as f:
            lines = f.read().decode("utf-8", errors="replace").splitlines()

    print(f"[INFO] Parsing {len(lines)} records...")
    records = []
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2:
            raw_label, text = parts[0].strip(), parts[1].strip()
            # Mapping logic
            # ham -> legitimate, spam -> other_suspicious
            if raw_label.lower() == "ham":
                label = "legitimate"
            elif raw_label.lower() == "spam":
                label = "other_suspicious"
            else:
                label = "other_suspicious"

            records.append({
                "text": text,
                "label": label,
                "channel": "sms",
                "language": "en",
                "source": "uci_sms",
                "original_label": raw_label
            })

    df = pd.DataFrame(records)
    print(f"[INFO] Parsed {len(df)} total SMS records.")
    print("[INFO] Label distribution:\n", df["label"].value_counts().to_string())

    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"[SUCCESS] Saved processed UCI SMS dataset to: {output_path}")
    return df


if __name__ == "__main__":
    download_and_process_uci_sms()
