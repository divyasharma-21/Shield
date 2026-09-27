SentryMesh ReportGuard UI fix

Replace these files in your existing package_source, preserving the rest of the project:
- backend/app/reporting.py
- backend/app/main.py
- frontend/src/App.tsx
- frontend/src/index.css

Changes:
- ReportGuard now returns and renders the sanitized report.
- Shows quarantine receipt/status/source/training boundary.
- Shows exact PII redaction counts and reasons.
- Shows observed security evidence with explanations.
- Preserves and displays security URLs.
- Shows sanitized reviewer note.
- Shows explicit PENDING MODERATOR REVIEW state.
- Adds empty-input and consent validation in the UI.
- No original raw report is persisted by ReportGuard.
