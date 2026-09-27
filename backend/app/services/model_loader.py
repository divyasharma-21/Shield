"""Thread-safe singleton model loader for SentryMesh V4 binary fraud model.

Strictly loads the real trained joblib pipeline and metrics JSON.
Fails visibly if either file is missing.
Never provides mock, fallback, or hardcoded models.
"""

from pathlib import Path
import json
import threading
from typing import Any, Tuple
import joblib

from app.config import settings


class ModelLoader:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.model: Any = None
        self.selected_threshold: float = 0.0
        self.model_name: str = "sentrymesh_binary_tfidf_v4"
        self.is_loaded: bool = False
        self.classes: list = []
        self.suspicious_class_index: int = 1

    @classmethod
    def get_instance(cls) -> "ModelLoader":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def load_artifacts(self) -> None:
        """Loads the trained V4 joblib model and metrics file.

        Raises FileNotFoundError with explicit diagnostic paths if either is missing.
        Raises ValueError if threshold cannot be parsed.
        """
        if self.is_loaded:
            return

        with self._lock:
            if self.is_loaded:
                return

            model_path: Path = settings.model_path
            metrics_path: Path = settings.metrics_path

            if not model_path.exists():
                raise FileNotFoundError(
                    f"CRITICAL CONFIGURATION ERROR: SentryMesh V4 model artifact not found at:\n"
                    f"  {model_path}\n"
                    f"Please ensure the file exists at <project_root>/models/sentrymesh_binary_tfidf_v4.joblib "
                    f"or set SENTRYMESH_MODEL_PATH in the environment."
                )

            if not metrics_path.exists():
                raise FileNotFoundError(
                    f"CRITICAL CONFIGURATION ERROR: SentryMesh V4 metrics file not found at:\n"
                    f"  {metrics_path}\n"
                    f"Please ensure the file exists at <project_root>/reports/sentrymesh_binary_tfidf_v4_metrics.json "
                    f"or set SENTRYMESH_METRICS_PATH in the environment."
                )

            # Load metrics first to read the dynamically selected threshold
            try:
                with open(metrics_path, "r", encoding="utf-8") as f:
                    metrics_data = json.load(f)
            except Exception as e:
                raise ValueError(
                    f"Failed to read or parse metrics JSON at {metrics_path}: {e}"
                )

            threshold_val = metrics_data.get("selected_suspicious_threshold")
            if threshold_val is None:
                raise ValueError(
                    f"Key 'selected_suspicious_threshold' not found in {metrics_path}."
                )

            try:
                self.selected_threshold = float(threshold_val)
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Invalid threshold value '{threshold_val}' in {metrics_path}: {e}"
                )

            self.model_name = metrics_data.get("model_name", "sentrymesh_binary_tfidf_v4")

            # Load the joblib pipeline
            try:
                loaded_model = joblib.load(model_path)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load joblib model from {model_path}: {e}"
                )

            # Validate pipeline structure
            if not hasattr(loaded_model, "predict_proba"):
                raise TypeError(
                    f"Loaded model from {model_path} does not implement predict_proba."
                )

            if not hasattr(loaded_model, "classes_"):
                raise TypeError(
                    f"Loaded model from {model_path} does not expose classes_ attribute."
                )

            self.model = loaded_model
            self.classes = list(self.model.classes_)

            if "suspicious" not in self.classes:
                raise ValueError(
                    f"Expected 'suspicious' in model classes, found: {self.classes}"
                )

            self.suspicious_class_index = self.classes.index("suspicious")
            self.is_loaded = True


def get_model_loader() -> ModelLoader:
    loader = ModelLoader.get_instance()
    if not loader.is_loaded:
        loader.load_artifacts()
    return loader
