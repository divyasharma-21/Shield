"""Configuration management for SentryMesh Guardian backend.

Resolves repository root dynamically, loads environment variables,
and verifies model artifact paths.
"""

from pathlib import Path
import os
from typing import List


class Settings:
    def __init__(self):
        # Resolve project root dynamically from backend source directory
        # File path: .../backend/app/config.py -> parents[2] is project root (e.g. D:\SentryMesh\sentrymesh)
        self.backend_dir = Path(__file__).resolve().parents[1]
        self.app_dir = Path(__file__).resolve().parent

        # Candidate project roots
        candidates = [
            Path(__file__).resolve().parents[2],
            Path(__file__).resolve().parents[2] / "sentrymesh",
            Path.cwd(),
            Path.cwd() / "sentrymesh",
        ]

        self.project_root = candidates[0]
        for c in candidates:
            if (c / "models" / "sentrymesh_binary_tfidf_v4.joblib").exists():
                self.project_root = c
                break

        # Model and metrics paths
        env_model = os.getenv("SENTRYMESH_MODEL_PATH")
        if env_model:
            model_candidate = Path(env_model)
            if not model_candidate.is_absolute():
                model_candidate = (self.backend_dir / model_candidate).resolve()
            self.model_path = model_candidate
        else:
            self.model_path = self.project_root / "models" / "sentrymesh_binary_tfidf_v4.joblib"

        env_metrics = os.getenv("SENTRYMESH_METRICS_PATH")
        if env_metrics:
            metrics_candidate = Path(env_metrics)
            if not metrics_candidate.is_absolute():
                metrics_candidate = (self.backend_dir / metrics_candidate).resolve()
            self.metrics_path = metrics_candidate
        else:
            self.metrics_path = self.project_root / "reports" / "sentrymesh_binary_tfidf_v4_metrics.json"

        # CORS
        raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
        self.cors_origins: List[str] = [orig.strip() for orig in raw_origins.split(",") if orig.strip()]

        # Feature flags for optional audio modules
        self.enable_audio_transcription: bool = os.getenv(
            "ENABLE_AUDIO_TRANSCRIPTION", "false"
        ).strip().lower() in ("true", "1", "yes")

        self.enable_voice_authenticity: bool = os.getenv(
            "ENABLE_VOICE_AUTHENTICITY", "false"
        ).strip().lower() in ("true", "1", "yes")

        # Audio file restrictions
        try:
            self.max_audio_file_mb: int = int(os.getenv("MAX_AUDIO_FILE_MB", "20"))
        except ValueError:
            self.max_audio_file_mb = 20

    @property
    def max_audio_bytes(self) -> int:
        return self.max_audio_file_mb * 1024 * 1024


settings = Settings()
