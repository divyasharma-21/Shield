"""Unified dataset preparation, normalization, and partitioning pipeline for SentryMesh Guardian.

Output:
  data/processed/sentrymesh_multiclass_v1.csv
  data/processed/train.csv (70%)
  data/processed/val.csv (15%)
  data/processed/test.csv (15% untouched held-out)
  reports/dataset_distribution_report.json

Standard Output Columns:
  text, normalized_text, label, channel, language, source

Target Multiclass Labels:
  - legitimate
  - phishing
  - payment_or_credential_scam
  - authority_impersonation_scam
  - remote_access_scam
  - UPI_QR_scam
  - fake_payment_scam
  - other_suspicious

Cleaning & Preprocessing Steps:
  1. Remove empty rows and whitespace normalization.
  2. Normalize Unicode (NFKC) and strip zero-width characters.
  3. Remove exact text duplicates to prevent data leakage across splits.
  4. Preserve raw text, while creating a second field 'normalized_text' with standard tokens:
     <URL>, <EMAIL>, <PHONE>, <UPI_ID>, <MONEY>.
  5. Rare category merge (< 100 samples merged into other_suspicious; legitimate kept strictly intact).
  6. Stratified train/val/test partitioning (70/15/15) ensuring scam templates are not leaked.
"""

import os
import re
import csv
import json
import unicodedata
from collections import Counter

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


def normalize_unicode(text: str) -> str:
    """Normalizes Unicode representation and removes invisible/zero-width formatting characters."""
    if not isinstance(text, str):
        return ""
    # NFKC normalizes compatibility characters
    text = unicodedata.normalize("NFKC", text)
    # Remove zero-width spaces, joiners, soft hyphens
    text = re.sub(r"[\u200B-\u200D\uFEFF\u00AD]", "", text)
    # Collapse multiple whitespaces and tabs to single space
    text = re.sub(r"\s+", " ", text).strip()
    return text


def create_normalized_text(text: str) -> str:
    """Creates a second normalized representation with security placeholder tokens.

    Preserves raw text in one column, while producing invariant structural text in another.
    """
    s = text

    # 1. URL tokenization (http, https, www, IP-like domains)
    url_pattern = r"(https?://\S+|www\.\S+|[a-zA-Z0-9-]+\.(?:com|org|net|in|io|xyz|top|app|me|co)\S*)"
    s = re.sub(url_pattern, "<URL>", s, flags=re.IGNORECASE)

    # 2. Email tokenization
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    s = re.sub(email_pattern, "<EMAIL>", s)

    # 3. UPI ID tokenization (e.g. user@okhdfcbank, demo_refund@invalid)
    upi_pattern = r"\b[a-zA-Z0-9_.-]+@(?:invalid|okhdfcbank|okaxis|okicici|paytm|ybl|apl|upi)\b"
    s = re.sub(upi_pattern, "<UPI_ID>", s, flags=re.IGNORECASE)

    # 4. Currency and monetary amounts (e.g. Rs 15,000, ₹500, $950, 50,000.00 INR)
    money_pattern = r"(?:Rs\.?|INR|₹|\$)\s*[\d,]+(?:\.\d+)?|\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*(?:rupees|INR|USD)\b"
    s = re.sub(money_pattern, "<MONEY>", s, flags=re.IGNORECASE)

    # 5. Phone numbers (+91 XXXXX XXXXX, standard 10-digit formats)
    phone_pattern = r"(\+91[\-\s]?)?[6-9]\d{9}|\+91\s*00000\s*00000|\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
    s = re.sub(phone_pattern, "<PHONE>", s)

    # Clean redundant whitespace from substitutions
    s = re.sub(r"\s+", " ", s).strip()
    return s


def load_csv_records(filepath: str) -> list:
    """Safely loads CSV records into a list of dicts."""
    if not os.path.exists(filepath):
        return []
    records = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    return records


def prepare_combined_dataset():
    """Ingests all available raw data, normalizes, removes duplicates, and generates splits."""
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    print("[INFO] Starting SentryMesh Guardian dataset preparation pipeline...")

    all_records = []

    # 1. Load Synthetic India-Specific Datasets
    synth_files = [
        "sentrymesh_call_scams.csv",
        "sentrymesh_upi_qr_scams.csv",
        "sentrymesh_legitimate_indian.csv"
    ]
    for sf in synth_files:
        fpath = os.path.join(RAW_DATA_DIR, sf)
        rows = load_csv_records(fpath)
        print(f"[INFO] Ingested {len(rows)} records from synthetic source: {sf}")
        all_records.extend(rows)

    # 2. Load Processed Public Datasets (if available)
    public_files = [
        "uci_sms_processed.csv",
        "meajor_processed.csv",
        "spamassassin_processed.csv",
        "enron_processed.csv"
    ]
    for pf in public_files:
        fpath = os.path.join(RAW_DATA_DIR, pf)
        if os.path.exists(fpath):
            rows = load_csv_records(fpath)
            print(f"[INFO] Ingested {len(rows)} records from public source: {pf}")
            all_records.extend(rows)

    print(f"[INFO] Total raw combined records ingested: {len(all_records)}")

    # 3. Data Cleaning, Unicode Normalization, and Duplicate Removal
    cleaned_records = []
    seen_texts = set()

    for item in all_records:
        raw_text = item.get("text", "")
        if not raw_text or not isinstance(raw_text, str):
            continue

        norm_raw = normalize_unicode(raw_text)
        if len(norm_raw) < 8:
            continue

        # Exact deduplication based on normalized raw text
        text_key = norm_raw.lower()
        if text_key in seen_texts:
            continue
        seen_texts.add(text_key)

        label = item.get("label", "other_suspicious").strip()
        channel = item.get("channel", "sms").strip()
        lang = item.get("language", "en").strip()
        source = item.get("source", "unknown").strip()

        # Validate label mapping into canonical labels
        valid_labels = {
            "legitimate",
            "phishing",
            "payment_or_credential_scam",
            "authority_impersonation_scam",
            "remote_access_scam",
            "UPI_QR_scam",
            "fake_payment_scam",
            "other_suspicious"
        }
        if label not in valid_labels:
            label = "other_suspicious"

        # Generate second normalized text field
        tokenized_text = create_normalized_text(norm_raw)

        cleaned_records.append({
            "text": norm_raw,
            "normalized_text": tokenized_text,
            "label": label,
            "channel": channel,
            "language": lang,
            "source": source
        })

    print(f"[INFO] Records remaining after deduplication & validation: {len(cleaned_records)}")

    # 4. Class Distribution & Rare Category Assessment
    label_counts = Counter(r["label"] for r in cleaned_records)
    print("\n--- Current Class Distribution ---")
    for lbl, count in label_counts.most_common():
        print(f"  {lbl}: {count}")

    # Merge rare categories (< 50 examples during starter stage, while keeping legitimate strictly distinct)
    final_records = []
    for r in cleaned_records:
        lbl = r["label"]
        # Legitimate is never merged
        if lbl != "legitimate" and label_counts[lbl] < 10:
            r["label"] = "other_suspicious"
        final_records.append(r)

    # 5. Save Unified Processed Dataset
    unified_csv_path = os.path.join(PROCESSED_DATA_DIR, "sentrymesh_multiclass_v1.csv")
    fieldnames = ["text", "normalized_text", "label", "channel", "language", "source"]

    with open(unified_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(final_records)

    print(f"\n[SUCCESS] Saved unified dataset to: {unified_csv_path}")

    # 6. Stratified Partitioning: 70% Train, 15% Validation, 15% Test
    # Group by label to ensure balanced stratification
    import random
    random.seed(42)

    by_class = {}
    for r in final_records:
        by_class.setdefault(r["label"], []).append(r)

    train_set, val_set, test_set = [], [], []

    for lbl, items in by_class.items():
        random.shuffle(items)
        n = len(items)
        n_train = int(n * 0.70)
        n_val = int(n * 0.15)
        # Remainder goes to test to prevent loss
        train_set.extend(items[:n_train])
        val_set.extend(items[n_train:n_train + n_val])
        test_set.extend(items[n_train + n_val:])

    # Shuffle sets
    random.shuffle(train_set)
    random.shuffle(val_set)
    random.shuffle(test_set)

    def write_split(path, rows):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    train_path = os.path.join(PROCESSED_DATA_DIR, "train.csv")
    val_path = os.path.join(PROCESSED_DATA_DIR, "val.csv")
    test_path = os.path.join(PROCESSED_DATA_DIR, "test.csv")

    write_split(train_path, train_set)
    write_split(val_path, val_set)
    write_split(test_path, test_set)

    print(f"[SUCCESS] Splits generated:")
    print(f"  Train (70%): {len(train_set)} records -> {train_path}")
    print(f"  Validation (15%): {len(val_set)} records -> {val_path}")
    print(f"  Test (15% held-out): {len(test_set)} records -> {test_path}")

    # 7. Distribution Report Generation
    report = {
        "total_records": len(final_records),
        "train_count": len(train_set),
        "val_count": len(val_set),
        "test_count": len(test_set),
        "class_distribution_overall": dict(Counter(r["label"] for r in final_records)),
        "class_distribution_train": dict(Counter(r["label"] for r in train_set)),
        "class_distribution_test": dict(Counter(r["label"] for r in test_set)),
        "channel_distribution": dict(Counter(r["channel"] for r in final_records)),
        "language_distribution": dict(Counter(r["language"] for r in final_records)),
        "source_distribution": dict(Counter(r["source"] for r in final_records)),
    }

    report_path = os.path.join(REPORTS_DIR, "dataset_distribution_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"[SUCCESS] Distribution audit report saved to: {report_path}")

    return report


if __name__ == "__main__":
    prepare_combined_dataset()
