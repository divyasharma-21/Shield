"""Health and configuration verification router."""

from fastapi import APIRouter, Depends
from app.schemas import HealthResponse
from app.services.model_loader import get_model_loader, ModelLoader
from app.config import settings

router = APIRouter(prefix="/api/v1", tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health_status(loader: ModelLoader = Depends(get_model_loader)) -> HealthResponse:
    """Returns runtime model health, selected threshold, and audio feature states."""
    return HealthResponse(
        status="ok",
        model_loaded=loader.is_loaded,
        model_name=loader.model_name,
        selected_suspicious_threshold=loader.selected_threshold,
        audio_transcription_configured=settings.enable_audio_transcription,
        voice_authenticity_configured=settings.enable_voice_authenticity
    )
