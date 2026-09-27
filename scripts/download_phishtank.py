"""Downloader and parser for PhishTank Verified Phishing URLs feed.

Safety Rule:
  NEVER open, execute, or automatically crawl listed URLs directly.
  Used only for:
    - URL reputation checks in app/verifier.py
    - Lexical feature extraction (domain structure, path entropy, punycode)
    - LinkGuard offline matching
  DO NOT mix raw standalone URLs into text classifiers without surrounding context.
"""

import os
import sys
import urllib.request
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

PHISHTANK_URL = "http://data.phishtank.com/data/online-valid.csv"
RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
OUTPUT_CSV_PATH = os.path.join(RAW_DATA_DIR, "phishtank.csv")


def fetch_phishtank_feed(
    url: str = PHISHTANK_URL,
    api_key: str = None,
    output_path: str = OUTPUT_CSV_PATH,
    sample_limit: int = 10000
) -> pd.DataFrame:
    """Downloads or updates the PhishTank valid phishing URL feed safely.

    If an API key is configured (PHISHTANK_API_KEY), it uses an authenticated request
    as recommended by PhishTank developer policy to avoid rate-limiting.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    api_key = api_key or os.getenv("PHISHTANK_API_KEY")

    download_url = url
    if api_key:
        download_url = f"http://data.phishtank.com/data/{api_key}/online-valid.csv"
        print(f"[INFO] Using configured PhishTank API key for feed download.")
    else:
        print("[INFO] No PhishTank API key detected; using public rate-limited endpoint.")

    print(f"[INFO] Connecting to PhishTank feed endpoint: {download_url}...")
    headers = {
        "User-Agent": "phishtank/sentrymesh-guardian-threat-intel-collector"
    }

    req = urllib.request.Request(download_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
    except Exception as exc:
        print(f"[WARNING] Could not fetch PhishTank online feed: {exc}", file=sys.stderr)
        print("[INFO] Checking if a local cached phishtank.csv already exists...")
        if os.path.exists(output_path):
            print(f"[INFO] Found existing cached PhishTank file at {output_path}.")
            return pd.read_csv(output_path)
        else:
            print("[INFO] Generating minimal placeholder phishtank.csv with safe test records.")
            placeholder_df = pd.DataFrame([
                {
                    "phish_id": 9999901,
                    "url": "http://invalid.example/secure-login-account-update",
                    "phish_detail_url": "http://www.phishtank.com/phish_detail.php?phish_id=9999901",
                    "submission_time": "2026-09-25T00:00:00+00:00",
                    "verified": "yes",
                    "verification_time": "2026-09-25T00:00:00+00:00",
                    "online": "yes",
                    "target": "Example Online Banking"
                },
                {
                    "phish_id": 9999902,
                    "url": "http://suspicious-verify.example.org/banking/kyc-update",
                    "phish_detail_url": "http://www.phishtank.com/phish_detail.php?phish_id=9999902",
                    "submission_time": "2026-09-25T00:00:00+00:00",
                    "verified": "yes",
                    "verification_time": "2026-09-25T00:00:00+00:00",
                    "online": "yes",
                    "target": "Example Telecom Service"
                }
            ])
            placeholder_df.to_csv(output_path, index=False)
            return placeholder_df

    # Parse CSV into dataframe
    import io
    df = pd.read_csv(io.BytesIO(content))
    print(f"[INFO] PhishTank feed downloaded. Total records: {len(df)}")

    # Extract required fields and filter verified online entries
    if "verified" in df.columns:
        df = df[df["verified"].astype(str).str.lower() == "yes"]

    if sample_limit and len(df) > sample_limit:
        print(f"[INFO] Sampling {sample_limit} most recent active entries.")
        df = df.head(sample_limit)

    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"[SUCCESS] PhishTank feed saved safely to: {output_path}")
    return df


if __name__ == "__main__":
    fetch_phishtank_feed()
