"""Model loader and artifact cache manager for SentryMesh Guardian.

Provides single-instance memory-efficient loading of:
  - sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
  - Baseline LogisticRegression classifier
  - Multi-label Tactic model
  - Label mappings
"""

import os
import json
from typing import Dict, Any, Optional

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
MODELS_DIR = os.path.join(BASE_DIR, "models")


class ModelManager:
    def __init__(self):
        self.embedder = None
        self.classifier = None
        self.tactic_model = None
        self.label_mapping = {}
        self.tactic_mapping = []
        self.is_loaded = False
        self._load_metadata()

    def _load_metadata(self):
        """Loads label mappings and tactic catalog."""
        mapping_file = os.path.join(MODELS_DIR, "label_mapping.json")
        if os.path.exists(mapping_file):
            try:
                with open(mapping_file, "r", encoding="utf-8") as f:
                    self.label_mapping = json.load(f)
            except Exception:
                pass

        if not self.label_mapping:
            # Standard default classes
            classes = [
                "legitimate",
                "phishing",
                "payment_or_credential_scam",
                "authority_impersonation_scam",
                "remote_access_scam",
                "UPI_QR_scam",
                "fake_payment_scam",
                "other_suspicious"
            ]
            self.label_mapping = {
                "classes": classes,
                "label_to_id": {c: i for i, c in enumerate(classes)},
                "id_to_label": {i: c for i, c in enumerate(classes)}
            }

        tactic_file = os.path.join(MODELS_DIR, "tactic_mapping.json")
        if os.path.exists(tactic_file):
            try:
                with open(tactic_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tactic_mapping = data.get("tactics", [])
            except Exception:
                pass

        if not self.tactic_mapping:
            self.tactic_mapping = [
                "authority_impersonation",
                "urgency",
                "fear_or_threat",
                "secrecy",
                "isolation",
                "payment_request",
                "otp_request",
                "credential_request",
                "remote_access_request",
                "screen_share_request",
                "upi_collect_request"
            ]

    def load_models_if_needed(self):
        """Lazy loads ML checkpoints into memory."""
        if self.is_loaded:
            return

        try:
            import joblib
            from sentence_transformers import SentenceTransformer

            # 1. Embedding model
            model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            self.embedder = SentenceTransformer(model_name)

            # 2. Main classifier
            clf_path = os.path.join(MODELS_DIR, "classifier.joblib")
            if os.path.exists(clf_path):
                data = joblib.load(clf_path)
                if isinstance(data, dict) and "model" in data:
                    self.classifier = data["model"]

            # 3. Tactic model
            tactic_path = os.path.join(MODELS_DIR, "tactic_model.joblib")
            if os.path.exists(tactic_path):
                t_data = joblib.load(tactic_path)
                if isinstance(t_data, dict) and "model" in t_data:
                    self.tactic_model = t_data["model"]

            self.is_loaded = True
        except Exception:
            # Fallback for lightweight runtime without PyTorch installed
            self.is_loaded = True

    def get_classes(self) -> list:
        return self.label_mapping.get("classes", [])

    def get_tactics(self) -> list:
        return self.tactic_mapping


_model_manager_instance = None

def get_model_manager() -> ModelManager:
    global _model_manager_instance
    if _model_manager_instance is None:
        _model_manager_instance = ModelManager()
    return _model_manager_instance
