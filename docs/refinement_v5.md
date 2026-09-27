# SentryMesh Refinement v5

## What changed

SentryMesh now uses a versioned ML intelligence layer rather than a single generic score path.

### MessageGuard v5
- Preserves the existing SentryMesh corpora and V4 artifacts.
- Adds real UCI SMS Spam Collection data and the existing real-email corpus.
- Removes exact duplicate text before training.
- Uses word + character TF-IDF with a class-balanced probabilistic linear classifier.
- Keeps a frozen operating threshold in the model artifact.
- Produces model-level positive and counter-evidence using learned feature contributions.
- Supports SMS, WhatsApp-style, email, social and payment inputs through the same learned core, with channel-specific reporting/actions.
- Adds a separately trained tactic model so the explanation layer is not a hard-coded list of keywords.

The UCI SMS Spam Collection contains 5,574 real SMS messages and is CC BY 4.0. Source: UCI Machine Learning Repository.

### ParentGuardian v1
ParentGuardian was separated from the fraud classifier because the earlier fraud-oriented model missed threat, harassment, coercion and unsafe-image patterns.

The new model predicts communication-safety categories:
- benign
- harassment
- threat
- coercion/blackmail
- secrecy/isolation
- unsafe image request
- location/meetup risk
- financial scam
- remote-access social engineering
- grooming-risk communication pattern

Training uses:
- SentryMesh-reviewed safety/tactic examples
- explicitly labelled synthetic safety augmentation
- real benign SMS/email examples as negative safety examples

The synthetic portion is explicitly marked in the training metadata. There is no claim that synthetic-domain evaluation represents real-world grooming/abuse prevalence. ParentGuardian describes observable communication patterns and does not diagnose abuse, grooming, intent, mental health or criminality.

Public safety datasets such as Jigsaw Toxic Comment and published cyberbullying/grooming datasets were reviewed as future external validation candidates, but data was not silently downloaded or mixed into training without a reproducible license/source record.

### AppGuard
AppGuard now has an app-name discovery layer backed by a curated metadata catalog. If a known app is entered alone, SentryMesh fills known package/publisher/store/capability metadata and then analyzes it.

If an app name is not found and no metadata is supplied, AppGuard returns **insufficient metadata** and does not invent a package, publisher, permission set or reputation score.

Remote-access capability is not automatically treated as malware. The report distinguishes legitimate remote-support functionality from risky usage context.

### WebGuard
- Fixed multi-label public-suffix handling for domains such as `sbi.co.in`.
- Added explicit `@`/userinfo-obfuscation evidence.
- Added a complete explainable score-component report.
- Preserves the PhiUSIIL trained model path and never fabricates webpage-only features.

PhiUSIIL is a real public dataset with 235,795 URL/webpage examples and 54 features, licensed CC BY 4.0 by UCI.

### Explainability contract
Every upgraded analysis should expose:
1. decision and numerical score;
2. operating threshold where applicable;
3. decision margin/uncertainty;
4. model/version;
5. learned evidence or metadata drivers;
6. extracted entities;
7. tactic/safety-category probabilities when available;
8. counter-evidence where available;
9. recommended defensive actions;
10. limitations and what the model did not observe.

A score is never presented as proof of maliciousness.

## Evaluation notes

`reports/messageguard_v5_metrics.json` records the training/holdout metrics. `reports/parentguardian_safety_v1_metrics.json` records the model composition and validation. ParentGuardian's synthetic augmentation means its reported test score should not be represented as real-world performance.

`reports/refinement_challenge_results.json` contains a small targeted regression suite based on the known failure cases from development. It is a regression check, not an independent benchmark.

## Dataset/source provenance

- UCI SMS Spam Collection — CC BY 4.0 — https://archive.ics.uci.edu/dataset/228/sms%2Bspam%2Bcollection
- UCI PhiUSIIL Phishing URL Dataset — CC BY 4.0 — https://archive.ics.uci.edu/dataset/967/phiusiil%2Bphishing%2Burl%2Bdataset
- Jigsaw Toxic Comment datasets — reviewed as a potential external safety validation source; not silently included without a reproducible download/license record.
- Android/Google Play metadata documentation — used to define what app provenance and permission metadata should be represented; not treated as a maliciousness verdict.
