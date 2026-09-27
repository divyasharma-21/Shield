"""Per-prediction feature attribution service for SentryMesh V4 model.

Extracts real linear feature contributions from TF-IDF sparse activations
and learned Logistic Regression coefficients.
Never fabricates features, and uses no keyword rules.
"""

from typing import Dict, Any, List
from app.schemas import EvidenceItem, ModelEvidence


def compute_model_attribution(model: Any, text: str) -> ModelEvidence:
    """Computes exact linear contributions for active features in the input text.

    Pipeline access:
      vectorizer = model.named_steps["tfidf"]
      classifier = model.named_steps["classifier"]

    Linear contribution formula:
      contribution = tfidf_value * learned_classifier_coefficient

    Binary coefficient orientation explanation:
      In scikit-learn binary Logistic Regression, classifier.coef_ has shape (1, n_features).
      The single row coef_[0] models log-odds for classifier.classes_[1].
      - If classifier.classes_[1] == 'suspicious':
          Positive coefficients directly increase log-odds of 'suspicious'.
      - If classifier.classes_[0] == 'suspicious':
          Coefficients are multiplied by -1 so positive contribution consistently
          denotes pull toward 'suspicious'.
    """
    if "tfidf" not in model.named_steps or "classifier" not in model.named_steps:
        raise ValueError(
            "Model pipeline does not contain required steps 'tfidf' and 'classifier'."
        )

    vectorizer = model.named_steps["tfidf"]
    classifier = model.named_steps["classifier"]

    # 1. Transform text through the loaded vectorizer to get sparse TF-IDF activations
    sparse_vector = vectorizer.transform([text])

    # 2. Get active feature indices (only non-zero features)
    non_zero_indices = sparse_vector.nonzero()[1]
    if len(non_zero_indices) == 0:
        return ModelEvidence(
            signals_favoring_suspicious=[],
            signals_favoring_legitimate=[]
        )

    # 3. Retrieve vocabulary feature names
    feature_names = vectorizer.get_feature_names_out()

    # 4. Handle binary coefficient orientation dynamically from classifier.classes_
    classes = list(classifier.classes_)
    if len(classes) != 2:
        raise ValueError(f"Expected binary classifier with 2 classes, got {len(classes)}.")

    if classes[1] == "suspicious":
        suspicious_coef = classifier.coef_[0]
    elif classes[0] == "suspicious":
        suspicious_coef = -classifier.coef_[0]
    else:
        raise ValueError(f"'suspicious' class not found in classifier.classes_: {classes}")

    # 5. Calculate contribution for each active feature: contribution = tfidf * coef
    suspicious_signals: List[EvidenceItem] = []
    legitimate_signals: List[EvidenceItem] = []

    for idx in non_zero_indices:
        tfidf_val = float(sparse_vector[0, idx])
        coef_val = float(suspicious_coef[idx])
        contribution = tfidf_val * coef_val
        feature_name = str(feature_names[idx])

        # Positive contribution pulls towards 'suspicious'
        # Negative contribution pulls towards 'legitimate'
        if contribution > 0:
            suspicious_signals.append(
                EvidenceItem(
                    feature=feature_name,
                    contribution=round(contribution, 4)
                )
            )
        elif contribution < 0:
            legitimate_signals.append(
                EvidenceItem(
                    feature=feature_name,
                    contribution=round(contribution, 4)
                )
            )

    # 6. Sort and extract top 5
    # Positive contributions sorted descending (strongest suspicious push first)
    suspicious_signals.sort(key=lambda x: x.contribution, reverse=True)
    top_suspicious = suspicious_signals[:5]

    # Negative contributions sorted ascending (most negative first, strongest legitimate pull)
    legitimate_signals.sort(key=lambda x: x.contribution)
    top_legitimate = legitimate_signals[:5]

    return ModelEvidence(
        signals_favoring_suspicious=top_suspicious,
        signals_favoring_legitimate=top_legitimate
    )
