# SentryMesh Guardian 🛡️

**AI-Powered Cybersecurity Defense Engine for Anti-Phishing, Scam Detection, and Fraud Prevention**

SentryMesh Guardian protects everyday citizens, students, senior citizens, and professionals from sophisticated modern cyber attacks: SMS smishing, spear-phishing emails, digital arrest / authority impersonation calls, fake payment confirmations, UPI / dynamic QR fraud, rogue remote access tools, and password-harvesting sites.

---

## 🧭 Core Architectural Philosophy

SentryMesh Guardian follows a strict six-stage cognitive defense cycle:

```
[ Observe ] ──▶ [ Detect ] ──▶ [ Analyse ] ──▶ [ Explain ] ──▶ [ Respond ] ──▶ [ Learn ]
```

1. **Observe**: Securely ingest user-submitted suspicious text, communication channels (SMS, WhatsApp, Email, Phone Call Transcript, UPI/QR request, App prompt), and contextual signals with explicit user consent.
2. **Detect**: Multi-stage classification leveraging multilingual semantic embeddings (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) and calibrated models to distinguish legitimate communication from scam vectors.
3. **Analyse**: Extract key indicators of compromise (IOCs)—sanitized domains, unshortened URLs, emails, phone tokens, UPI handles, currency amounts—and cross-examine with live reputation feeds (PhishTank, safe domain registries) and a multi-label cognitive tactic detector.
4. **Explain**: Provide evidence-based, human-readable explanations highlighting psychological manipulation tactics (urgency, isolation, authority intimidation, secret OTP solicitation) without opaque black-box verdicts.
5. **Respond**: Deliver immediate actionable mitigation steps (e.g., "Do not enter UPI PIN", "Report to Cyber Crime 1930 / cybercrime.gov.in", "Disconnect remote desktop session immediately").
6. **Learn**: Ethically aggregate anonymized threat patterns with strict privacy-by-design and mandatory human moderator review prior to any model retraining.

---

## ⚖️ Safety, Privacy & Ethical Guardrails

- **Zero Hardcoded Shortcuts**: We do not rely on naive rules like *"If text has 'OTP', it is scam"*. Real bank alerts contain OTPs, KYC reminders, and transaction alerts. SentryMesh models context and intent.
- **No Defamation**: We never declare a person to be a "criminal" or claim to ascertain an unknown caller's identity. Signals are labeled objectively: `high-risk pattern`, `reported suspicious`, `needs verification`, or `known threat match`.
- **No Accent or Dialect Bias**: Dialect, voice pitch, grammar, confidence, or unknown telephone prefixes are never treated as proof of fraud.
- **Privacy by Design**:
  - Zero storage of raw user messages or media by default.
  - Automatic client/pipeline masking of PII (names, Aadhaar, PAN, bank accounts, raw mobile numbers).
  - No automated ingestion of unvetted user telemetry into training sets.
- **Safe Synthetic Data**: All training benchmarks use synthetic placeholders:
  - Domains: `example.com`, `example.org`, `invalid.example`
  - UPI IDs: `demo_refund@invalid`, `demo_payment@invalid`
  - Numbers: `+91 00000 00000`
  - Fictional entities: `Example Bank`, `Demo College`, `Sample Courier`, `RemoteAssistDemo`

---

## 📁 Repository Directory Structure

```
sentrymesh/
├── README.md                           # Master project guide & architecture overview
├── requirements.txt                    # Python environment dependencies
├── .gitignore                          # Security-hardened git exclusion rules
├── .env.example                        # Template for environment variables (API keys, ports)
├── app/
│   ├── __init__.py
│   ├── main.py                         # FastAPI REST application entrypoint
│   ├── model_loader.py                 # Lazy loading & caching of embeddings/classifiers
│   ├── analyzer.py                     # Unified orchestration: pipeline coordinator
│   ├── extractor.py                    # Entity & IOC extractor (URLs, UPI IDs, amounts, PII)
│   ├── verifier.py                     # Live reputation verifier (domain, PhishTank, URL heuristics)
│   ├── response_engine.py              # Actionable guidance & safe countermeasure generator
│   ├── reporting.py                    # Privacy-preserving anonymized report collector
│   └── schemas.py                      # Pydantic data contracts (input/output validation)
├── notebooks/
│   ├── 01_download_public_data.ipynb   # Colab/Kaggle guide for public datasets
│   ├── 02_create_synthetic_data.ipynb  # Synthetic generation with safe placeholder rules
│   ├── 03_prepare_combined_dataset.ipynb# Ingestion, deduplication, and normalization pipeline
│   ├── 04_train_baseline_model.ipynb   # MiniLM multilingual embeddings + LogisticRegression
│   ├── 05_train_tactic_model.ipynb     # Multi-label psychological tactic detector
│   ├── 06_finetune_xlmr_lora.ipynb     # XLM-RoBERTa parameter-efficient LoRA fine-tuning
│   └── 07_evaluate_model.ipynb         # Rigorous metrics, slice evaluation, confusion matrix
├── scripts/
│   ├── download_uci_sms.py             # Automated fetcher for UCI SMS Spam dataset
│   ├── download_phishtank.py           # PhishTank offline feed ingestion & cache
│   ├── prepare_dataset.py              # Multiclass normalization & train/val/test splitter
│   ├── create_synthetic_data.py        # India-specific scam & legitimate contrast generator
│   ├── train_baseline.py               # Headless baseline training script
│   ├── train_tactic_model.py           # Headless tactic multi-label training script
│   └── evaluate_model.py               # Per-class F1, confusion matrix, slice audit script
├── data/
│   ├── raw/                            # Immutable raw source datasets
│   ├── processed/                      # Cleaned, unified, and partitioned training sets
│   └── samples/                        # Safe verified examples for integration tests
├── models/                             # Serialized weights, label encoders, checkpoints
├── reports/                            # Evaluation charts, confusion matrices, error audits
├── tests/                              # Pytest test suite covering regex, API, and pipelines
└── docs/
    ├── architecture.md                 # Deep-dive system architecture specification
    ├── data_sources.md                 # Provenance, licensing, attribution & data inventory
    ├── model_card.md                   # Model evaluation, limitations, and ethical considerations
    └── privacy_and_safety.md           # PII redaction protocols, moderator policy, safety bounds
```

---

## 🚀 Quickstart

### 1. Environment Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Generate Data & Train Baseline
```bash
python scripts/download_uci_sms.py
python scripts/create_synthetic_data.py
python scripts/prepare_dataset.py
python scripts/train_baseline.py
python scripts/train_tactic_model.py
```

### 3. Launch Backend API
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
## ParentGuardian audio recording and transcription

ParentGuardian now supports voluntary in-browser microphone recording. The browser creates a WebM recording only after the user presses **Start recording** and stops it when the user presses **Stop recording**. SentryMesh does not intercept or record calls in the background.

For server-side transcription, install the optional speech-to-text dependency and enable the feature in the backend environment:

```powershell
pip install -r backend/requirements-optional.txt
$env:ENABLE_AUDIO_TRANSCRIPTION="true"
```

The first transcription request may download the configured `faster-whisper` model. If transcription is not configured, the API returns an honest `501 not_configured` response rather than fabricating a transcript or deepfake score.

## Explainable evidence

WebGuard now returns an explicit score ledger under `explainable_report.evidence_items`. Each score-driving item identifies its contribution, reason, and evidence source. AppGuard distinguishes a verified/known catalog match from an unverified application and withholds a numeric score when identity evidence is insufficient. The shared frontend evidence map renders these nested structures instead of assuming a flat list.

## ReportGuard quarantine

ReportGuard requires explicit consent before storage. Common personal identifiers are redacted server-side, while security URLs and other threat indicators are retained where possible. Only the sanitized representation is persisted in the quarantine boundary; reports are marked `pending_moderator_review` and are blocked from automatic training ingestion.

