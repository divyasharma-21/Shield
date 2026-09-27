# SentryMesh Binary Model Comparison

## Evaluation dataset

- Dataset: `sentrymesh_challenge_test.csv`
- Total examples: 28
- Legitimate examples: 6
- Suspicious examples: 22
- Purpose: Independent development challenge evaluation

## Version 1

- Model: `sentrymesh_binary_tfidf_v1.joblib`
- Challenge accuracy: 92.86%
- Suspicious recall: 100.00%
- False negatives: 0
- False positives: 2
- Assessment: Highest scam-detection sensitivity. Preferred for a safety-first alerting workflow.

## Version 2

- Model: `sentrymesh_binary_tfidf_v2.joblib`
- Challenge accuracy: 75.00%
- Suspicious recall: 68.18%
- False negatives: 7
- False positives: 0
- Assessment: Rejected. Generic UCI SMS data reduced performance on SentryMesh-specific fraud patterns.

## Version 3

- Model: `sentrymesh_binary_tfidf_v3.joblib`
- Challenge accuracy: 92.86%
- Suspicious recall: 90.91%
- False negatives: 2
- False positives: 0
- Assessment: Improved substantially over Version 2 and eliminated false positives, but still misses Kannada authority-impersonation and remote-access fraud examples.

## Key conclusion

SentryMesh prioritizes preventing high-harm fraud. False negatives are therefore more dangerous than false positives. Version 1 currently has the strongest safety-first result on this development challenge set, while Version 3 is a promising more precise model for further multilingual and remote-access training improvements.

## Evaluation integrity note

The 28-example challenge dataset is now a development challenge set because Version 3 improvements were guided by Version 2 error analysis. It must not be used as the final unseen test for later versions. A separate final holdout set should be created before Version 4 training begins.

## Version 4

- Model: `sentrymesh_binary_tfidf_v4.joblib`
- Training policy: TF-IDF and logistic regression with validation-selected safety threshold.
- Selected suspicious threshold: 0.40
- Internal held-out test accuracy: 95.59%
- Internal suspicious recall: 99.02%
- Development challenge accuracy: 100.00% (28 of 28)
- Development challenge suspicious recall: 100.00% (22 of 22)
- Development challenge false negatives: 0
- Development challenge false positives: 0
- Assessment: Current best development result. The safety-first 0.40 threshold reduced missed suspicious examples while presenting ambiguous predictions as verification prompts rather than claims of certainty.

## Important limitation

The 28-example dataset is a development challenge set, not a final independent benchmark. V4 data design was informed by Version 2 and Version 3 errors on this set. A separate final holdout set must be created and kept out of model development before making any real-world performance claim.

## Version 4 Final Holdout Evaluation

- Frozen model: `sentrymesh_binary_tfidf_v4.joblib`
- Frozen suspicious threshold: `0.40`
- Final holdout dataset: `data/final_holdout/sentrymesh_final_holdout_v1.csv`
- Final holdout type: Independently generated, safely fictionalized synthetic evaluation data
- Final holdout examples: 100
- Exact normalized text overlap with V4 training data: 0
- Final-holdout accuracy: 86.00%
- Final-holdout suspicious precision: 87.84%
- Final-holdout suspicious recall: 92.86%
- Final-holdout suspicious F1 score: 90.28%
- False negatives: 5
- False positives: 9

### Safety interpretation

All 70 suspicious final-holdout examples received either `suspicious_needs_verification` or `uncertain_needs_verification`. No suspicious example received `no_strong_risk_signal`.

The five binary false negatives were near the 0.40 suspicious threshold and were shown as `uncertain_needs_verification`, not as guaranteed-safe messages.

### Limitations

The final holdout consisted of independently generated synthetic data and does not establish performance across all real-world scams, languages, channels, dialects, or adversarial messages. The model remains a text-based risk signal and must not be presented as proof that a caller, app, payment request, URL, or message is safe or fraudulent.
