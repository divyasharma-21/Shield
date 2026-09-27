# SentryMesh Guardian: Privacy, Ethics & Safety Guardrails

Privacy-by-Design and Non-Defamation principles are hard requirements embedded into every component of SentryMesh Guardian.

---

## 1. Non-Negotiable Operational Guardrails

### 1.1 Non-Defamation & Objectivity
- **NEVER** declare an individual, caller, or sender to be a "criminal".
- **NEVER** claim to ascertain a caller's true identity from an incoming number or unverified caller-ID.
- **NEVER** treat an unknown telephone number or unfamiliar email address as automatically fraudulent.
- **NEVER** treat voice, accent, dialect, grammatical imperfection, politeness, or confidence as proof of fraud.
- **Permitted Risk Terminology Only**:
  - `High-Risk Pattern Detected`
  - `Reported Suspicious`
  - `Needs Immediate Verification via Official Branch`
  - `Known Threat Vector Match`
  - `Unverified Domain / Untrusted Link`

### 1.2 Zero Shortcut Learning Rule
- **FORBIDDEN**: Hardcoded heuristic rules such as *"If a message contains 'OTP', label as scam."*
- Legitimate bank transaction confirmations, password resets, and Aadhaar OTPs contain words like "OTP", "bank", "KYC", "account", and "urgent".
- The system must evaluate semantic structure, psychological pressure, credential solicitation, and routing legitimacy—not single trigger words.

### 1.3 Offensive Tool Prohibition
- SentryMesh is strictly a **defensive technology**.
- We never generate operational phishing templates, deceptive landing pages, credential harvesters, functional malware, or weaponized QR codes.
- All testing assets, synthetic data, and documentation utilize non-routable dummy domains (`example.com`, `example.org`, `invalid.example`) and safe mock UPI handles (`*@invalid`).

---

## 2. Privacy by Design & PII Protection

### 2.1 Consent & Transient Ingestion
- User consent must be explicitly granted before processing any text or report.
- The API processes input text **in-memory** and does not persist raw message transcripts, audio recordings, or geolocations by default.
- Silent audio or background call interception is strictly prohibited.

### 2.2 PII Redaction Pipeline
Before any feature extraction or text vectorization:
- **Phone Numbers**: Redacted to `<PHONE>` or masked as `+91 XXXXX XX123`.
- **UPI IDs**: Redacted to `<UPI_ID>` or masked as `***@bank`.
- **Emails**: Redacted to `<EMAIL>`.
- **Financial Account Numbers / Card Numbers / Aadhaar / PAN**: Stripped immediately and replaced with `<REDACTED_FINANCIAL>`.
- **Monetary Amounts**: Normalized to `<MONEY>`.

### 2.3 Community Reporting & Quarantine Workflow
User reports can help track evolving campaigns, but:
1. **No Automatic Training**: Live user reports are **NEVER** fed directly into the model training pipeline.
2. **Moderator Review Gateway**:
   - Submissions land in an encrypted quarantine buffer (`data/user_reports/quarantine/`).
   - A qualified security moderator reviews the report for false positives, toxic spam, or intentional poisoning attempts.
   - PII is permanently purged.
3. **Public Views**:
   - Any public aggregated dashboards expose only anonymized campaign metadata (e.g., "Electricity Bill Scam targeting Western Region", "Domain spoofing registered under .tk").
   - Full telephone numbers, recipient details, screenshots, and reporter identity are never visible.
