# SentryMesh Final Holdout Protocol

## Purpose

This final holdout dataset is used only for final evaluation of the frozen SentryMesh Binary V4 model.

## Frozen model

- Model: `models/sentrymesh_binary_tfidf_v4.joblib`
- Selected suspicious threshold: `0.40`
- Training dataset: `data/processed/sentrymesh_binary_v4.csv`
- Development challenge dataset: `data/samples/sentrymesh_challenge_test.csv`

## Rules

1. Do not add final-holdout text to any training dataset.
2. Do not use final-holdout results to change V4 training data, TF-IDF settings, threshold, or model parameters.
3. Do not inspect final-holdout examples while creating Version 5 or later models.
4. Do not duplicate final-holdout examples from V1-V4 source datasets.
5. Do not include real victim names, account numbers, OTPs, UPI IDs, card details, phone numbers, live phishing URLs, malware links, or private messages.
6. Use only safely anonymized or fictionalized identifiers.
7. Record a source description and reviewer for every example.
8. Keep the final holdout dataset out of all model-training scripts.
9. Evaluate the frozen V4 model once.
10. If V4 is changed after viewing final-holdout results, create a new final holdout dataset for the new model version.

## Required CSV schema

id,text,label,channel,language,source,source_reference,reviewer,holdout_lock_date

## Binary labels

- `legitimate`
- `authority_impersonation_scam`
- `remote_access_scam`
- `UPI_QR_scam`
- `payment_or_credential_scam`
- `fake_payment_scam`

During binary evaluation, `legitimate` maps to legitimate and all other labels map to suspicious.

## Target composition

- 30 legitimate messages
- 15 authority-impersonation scams
- 15 remote-access scams
- 15 UPI or QR scams
- 15 payment or credential scams
- 10 fake-payment scams

Target total: 100 examples.

## Integrity statement

The final holdout must remain separate from all model development. The final report must disclose the sample size, category distribution, data sources, language distribution, selected threshold, suspicious recall, false negatives, false positives, and limitations.
