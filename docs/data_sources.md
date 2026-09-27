# SentryMesh Guardian: Data Sources & Provenance Register

This document tracks all external and synthetic data sources utilized across SentryMesh Guardian, their licensing constraints, intended roles in the ML pipeline, and strict PII / personal data risk assessments.

---

## 1. Public Datasets Register

### 1.1 UCI Machine Learning Repository: SMS Spam Collection
- **Dataset Name**: SMS Spam Collection
- **Source URL**: `https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip`
- **Date Downloaded / Referenced**: 2026-09-25
- **Licence / Terms to Check**: Creative Commons Attribution 4.0 International (CC BY 4.0) / Public Domain for Research.
- **Intended Use**: Benchmark training and validation for mobile SMS spam vs ham detection.
- **Redistribution Allowed**: Yes, with academic citation and attribution.
- **Attribution Requirements**:
  *Almeida, T.A., Gómez Hidalgo, J.M., Yamakami, A. (2011). Contributions to the Study of SMS Spam Filtering: New Collection and Results. ACM Symposium on Document Engineering (DocEng'11).*
- **Personal Data Risk**: Contains public SMS messages collected from Grumbletext UK and Singapore NUS SMS corpus. Numbers in raw text were partially anonymized, but legacy phone formats may exist; sanitized placeholders are applied in our pipeline.
- **Pipeline Stage**: Training and Testing (offline split).
- **Label Mapping**:
  - `ham` ➔ `legitimate`
  - `spam` ➔ `other_suspicious`
  - Meta: `channel=sms`, `language=en`, `source=uci_sms`

---

### 1.2 MeAJOR Phishing Email Dataset
- **Dataset Name**: MeAJOR (Multi-lingual / English Phishing Email Corpus)
- **Source URL**: `https://zenodo.org/records/18471483`
- **Date Downloaded / Referenced**: User-managed manual download (Zenodo repository)
- **Licence / Terms to Check**: Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Intended Use**: Ingestion of modern email phishing attacks and benign institutional communications.
- **Redistribution Allowed**: Check Zenodo specific version terms; raw dataset is kept in local `.gitignore` path `data/raw/meajor.csv`.
- **Attribution Requirements**: Cite the Zenodo DOI publication and creators.
- **Personal Data Risk**: May contain scraped email headers or synthetic campaign targets. PII redaction and regex tokenization must be executed upon raw ingestion.
- **Pipeline Stage**: Training and Testing.
- **Label Mapping**:
  - `0` / `benign` ➔ `legitimate`
  - `1` / `phishing` ➔ `phishing`
  - Meta: `channel=email`, `language=en`, `source=meajor`
  - Subsetting: Initial balanced sample of 1,500 legitimate + 1,500 phishing records.

---

### 1.3 Apache SpamAssassin Public Corpus
- **Dataset Name**: Apache SpamAssassin Public Mail Corpus
- **Source URL**: `https://spamassassin.apache.org/old/publiccorpus/`
- **Date Downloaded / Referenced**: Documented manual download guide (e.g. `20030228_easy_ham.tar.bz2`, `20030228_spam.tar.bz2`)
- **Licence / Terms to Check**: Apache License 2.0 / Public open email collection for anti-spam filtering research.
- **Intended Use**: Training legitimate contrast emails and traditional junk/scam emails.
- **Redistribution Allowed**: Yes, according to Apache open-source distribution terms.
- **Attribution Requirements**: Apache SpamAssassin Project.
- **Personal Data Risk**: Contains historical public mailing list emails (primarily Linux kernel, open-source mailing lists) from the early 2000s. Contains real email addresses from that era. Our parser redacts email addresses into `<EMAIL>`.
- **Pipeline Stage**: Training and Testing.
- **Label Mapping**:
  - `ham` ➔ `legitimate`
  - `spam` ➔ `other_suspicious`
  - Meta: `channel=email`, `language=en`, `source=spamassassin`

---

### 1.4 Enron Email Dataset
- **Dataset Name**: Enron Email Corpus (CMU / FERC Public Release)
- **Source URL**: `https://www.cs.cmu.edu/~./enron/`
- **Date Downloaded / Referenced**: Documented manual download; local extraction to `data/raw/enron/`
- **Licence / Terms to Check**: Made public by the Federal Energy Regulatory Commission during its investigation; research use permitted.
- **Intended Use**: Exclusive use as legitimate contrast examples (`legitimate`) to prevent the model from assuming business or corporate language is fraudulent.
- **Redistribution Allowed**: Public academic dataset, but raw data is not committed to the repository.
- **Attribution Requirements**: William W. Cohen (CMU) Enron Email Dataset.
- **Personal Data Risk**: Historic employee corporate communications. Extracted body text is sampled (1,000–3,000 records) and stripped of private identifiable metadata.
- **Pipeline Stage**: Training and Testing (legitimate class anchor).
- **Label Mapping**:
  - `label=legitimate`
  - Meta: `channel=email`, `language=en`, `source=enron`

---

### 1.5 PhishTank Phishing URL Feed
- **Dataset Name**: PhishTank Valid Phishes Feed
- **Source URL**: `http://data.phishtank.com/data/online-valid.csv`
- **Date Downloaded / Referenced**: Periodic refresh (manual or API-key based) saved to `data/raw/phishtank.csv`
- **Licence / Terms to Check**: OpenDNS / Cisco PhishTank Developer Terms of Use. Free for non-commercial security applications.
- **Intended Use**: Live verification and domain reputation checks in `app/verifier.py`, LinkGuard testing, and offline domain lexical feature extraction.
- **Redistribution Allowed**: Feed itself should not be re-hosted; cache locally.
- **Attribution Requirements**: PhishTank (cisco/opendns).
- **Personal Data Risk**: None. Contains only URLs and submission metadata.
- **Pipeline Stage**: **Live Verification Only** (never mixed raw into message text classification without surrounding context).
- **Safety Rule**: **NEVER** navigate to or open listed URLs directly.

---

## 2. Synthetic India-Specific Datasets (Reviewed & Controlled)

To bridge the gap where global public corpora omit regional attack vectors (e.g. UPI PIN scams, Electricity Bill disconnection scams, Digital Arrest, APK file side-loading, and KYC expiry threats), SentryMesh provides carefully curated synthetic datasets.

All synthetic data adheres to strict safety placeholder rules:
- **Domains**: `example.com`, `example.org`, `invalid.example`
- **UPI IDs**: `demo_refund@invalid`, `demo_payment@invalid`, `test_merchant@invalid`
- **Phone Numbers**: `+91 00000 00000`
- **Organizations**: `Example Bank`, `Demo College`, `Sample Courier`, `Test Telecom`, `Sample Cyber Office`
- **Remote Support Apps**: `RemoteAssistDemo`, `SupportDemo`, `ScreenHelpDemo`
- **Provenance Tag**: `source = synthetic_reviewed`

### Curated Files:
1. `data/raw/sentrymesh_call_scams.csv` (100 transcript examples of digital arrest, customs fraud, police impersonation, credit card limit scams)
2. `data/raw/sentrymesh_upi_qr_scams.csv` (100 UPI collect request scams, reverse QR payment traps, OLX buyer scams, lottery UPI tricks)
3. `data/raw/sentrymesh_legitimate_indian.csv` (150 contrast examples with words like OTP, KYC, refund, scholarship, bank, UPI, urgent, fee)
4. `data/raw/sentrymesh_tactics.csv` (100 multi-label tactic samples covering psychological levers)
