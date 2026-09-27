# SentryMesh Version 4 Plan

## Objective

Improve safety on multilingual authority-impersonation scams and remote-access scams while retaining low false-positive rates.

## Known Version 3 weaknesses

- Kannada authority-impersonation text was incorrectly predicted as legitimate.
- One remote-access/payment-support message was incorrectly predicted as legitimate.
- The model uses only TF-IDF text features and does not yet use tactic features, language detection, app reputation, URL reputation, or live payment verification.

## V4 data additions

- Add Kannada suspicious and legitimate examples.
- Add Hindi/Hinglish suspicious and legitimate examples.
- Add varied remote-access scam examples.
- Add varied legitimate support, delivery, and payment-related messages.
- Do not add exact development challenge examples to training data.

## V4 decision policy

- Train a binary text-risk classifier.
- Use calibrated probability estimates where feasible.
- Select the suspicious threshold using validation data, not the development challenge set.
- Present uncertain outputs as "needs verification".
- Never state that a text-only model has confirmed that a message is safe.
- Never request OTPs, UPI PINs, passwords, card details, screen sharing, or remote-access installation.

## Evaluation policy

- Keep `sentrymesh_challenge_test.csv` as the development challenge set.
- Create a different final holdout set before V4 training.
- Do not inspect final holdout contents during V4 data design.
- Compare false negatives, suspicious recall, and false positives across V1, V2, V3, and V4.
