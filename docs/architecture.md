# SentryMesh Guardian: Architecture Specification

## 1. System Overview

SentryMesh Guardian is an open, privacy-by-design cyber defense platform built to protect everyday users from multi-channel scams (SMS, Email, Calls/Audio Transcripts, Payment requests, UPI/Dynamic QR codes, and Rogue Applications).

The framework implements a strict six-stage cognitive lifecycle:
`Observe` ➔ `Detect` ➔ `Analyse` ➔ `Explain` ➔ `Respond` ➔ `Learn`

```
┌────────────────────────────────────────────────────────────────────────┐
│                        USER COMMUNICATION INGEST                       │
│    (SMS, WhatsApp, Email, Phone Transcript, UPI Request, QR payload)   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [1. OBSERVE]                                                           │
│  - Privacy Filter: Client-side / Ingestion PII Tokenization            │
│  - Text Normalization & Safe Placeholder Injection (<URL>, <UPI_ID>)  │
│  - Channel Meta Ingestion & Language Identification                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [2. DETECT] Multilingual Semantic Encoder & Calibrated Classification  │
│  - Model: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2  │
│  - Layer: Calibrated Multi-Class Classifier (Balanced LogReg / LoRA)   │
│  - Output: Category Probabilities & Uncertainty Metric                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [3. ANALYSE] IOC Extractor, Tactic Scorer & Threat Verification        │
│  - Entity Extraction: URLs, Domains, UPI IDs, Phone Numbers, Amounts   │
│  - Psychological Tactic Multi-Label Model (Urgency, Fear, Authority)   │
│  - Live Verification: PhishTank Offline/Online Feed, Domain Heuristics │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [4. EXPLAIN] Transparent Evidence Synthesis Engine                     │
│  - Translates Model Embeddings & Tactic Activations into Human Insights│
│  - Explains WHY an interaction is risky without technical jargon       │
│  - Strict Neutrality: No subjective insults or criminal accusations    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [5. RESPOND] Countermeasure & Safe Guidance Engine                     │
│  - Channel-specific immediate safety checklist                         │
│  - Emergency hotline integration (e.g. 1930 Cyber Fraud Helpline)     │
│  - UPI PIN Safety / App Disconnect guidance                            │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ [6. LEARN] Privacy-Preserving Feedback & Moderator Gateway             │
│  - User-consented anonymized report collection                         │
│  - Air-gapped moderation quarantine: NO automatic retraining           │
│  - Periodic audited synthetic & curated benchmark refreshes            │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Breakdown

### A. Extractor (`app/extractor.py`)
- Regex-driven IOC parsing designed specifically for Indian & International fraud vectors.
- Captures:
  - URLs and FQDNs (with punycode detection and IP-host identification).
  - UPI IDs (`username@bankhandle`, e.g. `*.okhdfcbank`, `*.paytm`, `*.ybl`).
  - Phone formats (`+91` formats, national numbers).
  - Currency amounts (₹, INR, Rs., USD, etc.).
- Normalizer: Produces sanitized `<URL>`, `<EMAIL>`, `<PHONE>`, `<UPI_ID>`, `<MONEY>` text representations to evaluate structural semantic invariant features.

### B. Verifier (`app/verifier.py`)
- Cross-references extracted domains with safe domain whitelists and PhishTank / blocklist feeds.
- Checks for homograph spoofing, suspicious TLDs (`.xyz`, `.top`, `.tk`), and raw IP hostnames.
- UPI validation: verifies known legitimate payment provider handles vs suspicious random strings.

### C. Model Loader & Analyzer (`app/model_loader.py` & `app/analyzer.py`)
- Single-instance memory-efficient loading of `paraphrase-multilingual-MiniLM-L12-v2`.
- Dual-head inferencing:
  1. **Primary Intent Classifier**: Assigns one of 8 multiclass labels (`legitimate`, `phishing`, `authority_impersonation_scam`, `UPI_QR_scam`, `payment_or_credential_scam`, `fake_payment_scam`, `remote_access_scam`, `other_suspicious`).
  2. **Multi-Label Tactic Model**: Identifies concurrent emotional and manipulative vectors (`urgency`, `authority_impersonation`, `fear_or_threat`, `secrecy`, `isolation`, `payment_request`, `otp_request`, `credential_request`, `remote_access_request`, `screen_share_request`, `upi_collect_request`).
- Calculates uncertainty: Measures entropy and margin between top prediction probabilities (`low`, `medium`, `high`).

### D. Response Engine (`app/response_engine.py`)
- Translates detected classes and active psychological tactics into immediate consumer safeguards.
- Example: If `remote_access_request` is active, immediately advises:
  *"Never install screen-sharing software like AnyDesk or QuickSupport at the instruction of an unknown caller. Legitimate bank officers never require remote phone access."*
