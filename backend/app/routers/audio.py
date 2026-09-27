"""Voluntary audio upload and transcription analysis router."""

from fastapi import APIRouter, UploadFile, File, Depends
from app.schemas import AudioAnalysisResponse
from app.services.audio_service import AudioService
from app.dependencies import get_audio_service

router = APIRouter(prefix="/api/v1/analyze/call", tags=["Audio"])


@router.post("/audio", response_model=AudioAnalysisResponse)
async def analyze_call_audio_endpoint(
    file: UploadFile = File(..., description="Uploaded audio file (wav, mp3, m4a, webm)"),
    service: AudioService = Depends(get_audio_service)
) -> AudioAnalysisResponse:
    """Analyzes voluntarily uploaded call audio.

    Privacy Guarantee:
    - Audio is saved temporarily, never retained, and deleted immediately after processing.
    - If transcription or anti-spoof models are unconfigured, returns HTTP 501 without fabrication.
    """
    text_analysis, voice_auth = await service.process_audio_upload(file)

    return AudioAnalysisResponse(
        module="parent_call_audio",
        status="analyzed",
        transcription_analysis=text_analysis,
        voice_authenticity_analysis=voice_auth
    )
