"""FastAPI route dependencies."""

from app.services.model_loader import get_model_loader, ModelLoader
from app.services.audio_service import audio_service, AudioService


def get_loaded_model_loader() -> ModelLoader:
    return get_model_loader()


def get_audio_service() -> AudioService:
    return audio_service
