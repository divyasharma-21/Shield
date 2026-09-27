"""Parser and sampler for the MeAJOR Phishing Email Dataset.

Instructions:
  1. Download the dataset manually from Zenodo:
     https://zenodo.org/records/18471483
  2. Save the downloaded CSV file to:
     data/raw/meajor.csv
  3. Run this script:
     python scripts/parse_meajor.py

This script:
  - Inspects and prints all column names in data/raw/meajor.csv.
  - Supports configurable environment variables or CLI flags for:
      MEAJOR_TEXT_COLUMN
      MEAJOR_LABEL_COLUMN
  - Maps:
      benign / 0 / 'ham'       -> legitimate
      phishing / 1 / 'phish'   -> phishing
  - Adds metadata:
      channel = email
      language = en
      source = meajor
  - Samples a balanced subset initially: 1500 legitimate + 1500 phishing records.
  - Generates safe mock data if the file is not yet downloaded.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
INPUT_CSV_PATH = os.path.join(RAW_DATA_DIR, "meajor.csv")
OUTPUT_CSV_PATH = os.path.join(RAW_DATA_DIR, "meajor_processed.csv")


def inspect_and_parse_meajor(
    input_path: str = INPUT_CSV_PATH,
    output_path: str = OUTPUT_CSV_PATH,
    text_col: str = None,
    label_col: str = None,
    sample_size_per_class: int = 1500
) -> pd.DataFrame:
    """Inspects and parses MeAJOR dataset with configurable column mapping."""
    text_col = text_col or os.getenv("MEAJOR_TEXT_COLUMN")
    label_col = label_col or os.getenv("MEAJOR_LABEL_COLUMN")

    if not os.path.exists(input_path):
        print(f"[NOTICE] MeAJOR dataset file not found at: {input_path}")
        print("----------------------------------------------------------------------")
        print("To use real MeAJOR data, please download it from Zenodo:")
        print("  URL: https://zenodo.org/records/18471483")
        print(f"  Save as: {os.path.abspath(input_path)}")
        print("----------------------------------------------------------------------")
        print("[INFO] Creating safe starter meajor.csv placeholder for initial testing...")

        sample_rows = [
            # Legitimate emails
            {"email_text": "Hi team, please find attached the quarterly product roadmap deck for discussion tomorrow.", "is_phishing": 0},
            {"email_text": "Dear Student, your semester examination hall ticket is now available for download on the college portal.", "is_phishing": 0},
            {"email_text": "Your monthly utility statement for account #4489 is ready. Total due is zero. Thank you for using auto-pay.", "is_phishing": 0},
            {"email_text": "Meeting invite: Project architecture review on Thursday at 3:00 PM in Conference Room B.", "is_phishing": 0},
            {"email_text": "Thank you for attending the engineering webinar. The slide presentation and session recording are attached.", "is_phishing": 0},
            # Phishing emails
            {"email_text": "CRITICAL: Your corporate email mailbox has exceeded quota. Verify your login credentials within 24 hours at http://invalid.example/verify or your account will be suspended.", "is_phishing": 1},
            {"email_text": "Dear Customer, an unauthorized transaction of $950 was initiated. If this was not you, cancel immediately at http://invalid.example/security-cancel", "is_phishing": 1},
            {"email_text": "Notice of Tax Refund: You have an unclaimed refund of $420. Submit your banking password and card details to claim at http://invalid.example/refund-gov", "is_phishing": 1},
            {"email_text": "IT Helpdesk: Mandatory security certificate upgrade required. Enter your Windows domain password at http://invalid.example/update-cert", "is_phishing": 1},
            {"email_text": "Your cloud storage subscription expired. Renew immediately by submitting your credit card number at http://invalid.example/renew-sub", "is_phishing": 1},
        ]
        os.makedirs(os.path.dirname(input_path), exist_ok=True)
        placeholder_df = pd.DataFrame(sample_rows)
        placeholder_df.to_csv(input_path, index=False)
        print(f"[INFO] Created placeholder at {input_path} with {len(placeholder_df)} sample rows.")

    df = pd.read_csv(input_path)
    print(f"\n[INFO] Loaded MeAJOR dataset from {input_path}")
    print(f"[INFO] Available Columns in file ({len(df.columns)}):")
    for idx, col in enumerate(df.columns):
        print(f"  [{idx}] {col}")

    # Heuristic column detection if not explicitly set
    if not text_col:
        possible_text = [c for c in df.columns if any(k in c.lower() for k in ["text", "body", "email", "content", "message"])]
        text_col = possible_text[0] if possible_text else df.columns[0]
        print(f"[INFO] Auto-selected text column: '{text_col}'. (Override with MEAJOR_TEXT_COLUMN env var)")

    if not label_col:
        possible_label = [c for c in df.columns if any(k in c.lower() for k in ["label", "phish", "target", "class", "is_"])]
        label_col = possible_label[0] if possible_label else df.columns[-1]
        print(f"[INFO] Auto-selected label column: '{label_col}'. (Override with MEAJOR_LABEL_COLUMN env var)")

    # Mapping logic
    def map_meajor_label(val):
        val_str = str(val).strip().lower()
        if val_str in ["0", "benign", "legitimate", "ham", "normal", "false"]:
            return "legitimate"
        elif val_str in ["1", "phishing", "phish", "spam", "true", "malicious"]:
            return "phishing"
        return "other_suspicious"

    processed = pd.DataFrame()
    processed["text"] = df[text_col].dropna().astype(str).str.strip()
    processed["label"] = df[label_col].apply(map_meajor_label)
    processed["channel"] = "email"
    processed["language"] = "en"
    processed["source"] = "meajor"

    # Remove blanks
    processed = processed[processed["text"].str.len() > 10]

    # Balanced sampling: 1500 legitimate + 1500 phishing (or maximum available)
    legit_df = processed[processed["label"] == "legitimate"]
    phish_df = processed[processed["label"] == "phishing"]

    n_legit = min(len(legit_df), sample_size_per_class)
    n_phish = min(len(phish_df), sample_size_per_class)

    sampled_legit = legit_df.sample(n=n_legit, random_state=42) if n_legit > 0 else legit_df
    sampled_phish = phish_df.sample(n=n_phish, random_state=42) if n_phish > 0 else phish_df

    balanced_df = pd.concat([sampled_legit, sampled_phish], ignore_index=True)
    balanced_df = balanced_df.sample(frac=1.0, random_state=42).reset_index(drop=True)

    print(f"\n[INFO] Sampled Balanced MeAJOR Subset:")
    print(balanced_df["label"].value_counts().to_string())

    balanced_df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"[SUCCESS] Saved processed MeAJOR emails to: {output_path}")
    return balanced_df


if __name__ == "__main__":
    inspect_and_parse_meajor()
