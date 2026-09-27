"""Parser and sampler for the Enron Email Dataset.

Instructions:
  1. Download the Enron email dataset (e.g. from CMU):
     https://www.cs.cmu.edu/~./enron/
  2. Extract files into:
     data/raw/enron/maildir/
  3. Run this script:
     python scripts/parse_enron.py

Licensing & Usage Constraints:
  - Do NOT redistribute raw data without checking permissions.
  - Used EXCLUSIVELY as legitimate corporate contrast examples:
      label = legitimate
      channel = email
      language = en
      source = enron
  - Samples 1000–3000 records initially to prevent dataset skew.
  - All email addresses and telephone patterns are redacted.
"""

import os
import re
import email
from email import policy
import pandas as pd

RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
ENRON_DIR = os.path.join(RAW_DATA_DIR, "enron")
OUTPUT_CSV_PATH = os.path.join(RAW_DATA_DIR, "enron_processed.csv")


def extract_body(file_path: str) -> str:
    """Extracts body text from raw Enron mail file."""
    try:
        with open(file_path, "rb") as f:
            msg = email.message_from_binary_file(f, policy=policy.default)
            body = msg.get_body(preferencelist=('plain',))
            if body:
                return body.get_content().strip()
    except Exception:
        pass
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
            body_lines = []
            past_headers = False
            for line in lines:
                if not past_headers:
                    if line.strip() == "":
                        past_headers = True
                else:
                    body_lines.append(line)
            return "".join(body_lines).strip()
    except Exception:
        return ""


def sample_enron_legitimate(
    base_dir: str = ENRON_DIR,
    output_path: str = OUTPUT_CSV_PATH,
    sample_size: int = 1500
) -> pd.DataFrame:
    """Samples legitimate business contrast emails from Enron."""
    os.makedirs(base_dir, exist_ok=True)
    records = []
    found_files = False

    for root, _, files in os.walk(base_dir):
        for fname in files:
            if fname.startswith("."):
                continue
            fpath = os.path.join(root, fname)
            body = extract_body(fpath)
            if body and 50 < len(body) < 3000:
                # Privacy redaction
                sanitized = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", "<EMAIL>", body)
                sanitized = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "<PHONE>", sanitized)
                records.append({
                    "text": sanitized,
                    "label": "legitimate",
                    "channel": "email",
                    "language": "en",
                    "source": "enron"
                })
                found_files = True
                if len(records) >= sample_size:
                    break
        if len(records) >= sample_size:
            break

    if not found_files:
        print(f"[NOTICE] No raw Enron files found in: {base_dir}")
        print("----------------------------------------------------------------------")
        print("To load Enron legitimate corpus:")
        print("  1. Download archive from: https://www.cs.cmu.edu/~./enron/")
        print(f"  2. Untar into: {os.path.abspath(base_dir)}")
        print("----------------------------------------------------------------------")
        print("[INFO] Creating safe starter enron_processed.csv placeholder...")
        placeholder = [
            {"text": "Attached is the weekly power transmission schedule for the southern pipeline region. Please review by EOD.", "label": "legitimate", "channel": "email", "language": "en", "source": "enron"},
            {"text": "Good morning, the monthly accounting reconciliation spreadsheet has been uploaded to the shared network drive.", "label": "legitimate", "channel": "email", "language": "en", "source": "enron"},
            {"text": "Confirming our conference call tomorrow at 10 AM to discuss the pipeline maintenance contract renewal.", "label": "legitimate", "channel": "email", "language": "en", "source": "enron"},
            {"text": "Please see the updated travel and expense guidelines for Q3. Expense reports must be submitted before Friday.", "label": "legitimate", "channel": "email", "language": "en", "source": "enron"},
        ]
        df = pd.DataFrame(placeholder)
    else:
        df = pd.DataFrame(records)

    print(f"[INFO] Parsed Enron dataset. Total legitimate records: {len(df)}")
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"[SUCCESS] Saved to {output_path}")
    return df


if __name__ == "__main__":
    sample_enron_legitimate()
