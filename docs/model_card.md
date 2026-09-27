# SentryMesh Guardian: Model Card

## 1. Model Details
- **Model Name**: SentryMesh Multilingual Scam Classifier & Cognitive Tactic Detector
- **Version**: 1.0.0-baseline
- **Primary Backbone**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384-dimensional dense semantic representations)
- **Downstream Head**: Calibrated `LogisticRegression(max_iter=3000, class_weight='balanced')`
- **Tactic Multi-Label Head**: `MultiOutputClassifier(LogisticRegression(max_iter=2000, class_weight='balanced'))`
- **Optional Deep Head**: `FacebookAI/xlm-roberta-base` with PEFT (Parameter-Efficient Fine-Tuning) LoRA adapters (`r=16, lora_alpha=32, target_modules=["query", "value"]`).
- **Languages Supported**: English, Hindi, Hinglish, Kannada-English mixed, and code-mixed South Asian linguistic patterns.

---

## 2. Intended Use
- **Primary Intended Use**:
  Assisting end users in evaluating suspicious digital communications across SMS, WhatsApp, Email, Phone call transcripts, UPI payment links, and dynamic QR prompts.
- **Cognitive Tactics Evaluated**:
  - `authority_impersonation` (police, CBI, customs, telecom officials, electricity board)
  - `urgency` ("account will be blocked within 2 hours", "immediate action required")
  - `fear_or_threat` ("warrant issued", "FIR registered", "power disconnection")
  - `secrecy` ("do not tell anyone", "confidential verification")
  - `isolation` ("stay on video call", "do not disconnect")
  - `payment_request`
  - `otp_request`
  - `credential_request`
  - `remote_access_request` (AnyDesk, QuickSupport, TeamViewer)
  - `screen_share_request`
  - `upi_collect_request`
- **Out of Scope & Prohibited Uses**:
  - Autonomous criminal prosecution or judicial profiling.
  - Silent call interception or real-time lawful intercept wiretapping.
  - Automatic freezing of user bank accounts without banking verification.

---

## 3. Training & Evaluation Pipeline
- **Splits**: 70% Train, 15% Validation, 15% Held-out Test (stratified by class and language).
- **Core Datasets**:
  - UCI SMS Spam Collection
  - MeAJOR Phishing Corpus
  - Apache SpamAssassin Public Corpus
  - Enron Clean Corporate Corpus
  - Curated India-Specific Synthetic Datasets (`sentrymesh_call_scams.csv`, `sentrymesh_upi_qr_scams.csv`, `sentrymesh_legitimate_indian.csv`)
- **Key Metrics**:
  - Class-wise Precision, Recall, and F1 Score.
  - Macro and Weighted F1 Score.
  - Slice evaluation across communication channels (`sms`, `email`, `call`, `qr`) and linguistic subsets (`en`, `hi-en`, `kn-en`).
  - False positive rate on legitimate messages containing sensitive keywords (`OTP`, `KYC`, `bank`, `refund`).

---

## 4. Limitations & Mitigations
- **Adversarial Obfuscation**: Scammers may intentionally insert zero-width spaces, leetspeak, or misspellings.
  *Mitigation*: The pipeline applies Unicode normalization, homoglyph translation, and entity tokenization prior to embedding.
- **Zero-Shot Novel Scams**: Completely novel narrative scams may result in lower confidence.
  *Mitigation*: The system produces an explicit `uncertainty` metric (`low`, `medium`, `high`) and prompts user caution if confidence is borderline.
