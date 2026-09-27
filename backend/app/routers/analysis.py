"""Text and call-transcript risk analysis router."""

from fastapi import APIRouter, HTTPException, status
from app.schemas import TextAnalysisRequest, TextAnalysisResponse
from app.services.inference_service import analyze_text_content

router = APIRouter(prefix="/api/v1/analyze", tags=["Analysis"])


@router.post("/text", response_model=TextAnalysisResponse)
def analyze_text_endpoint(payload: TextAnalysisRequest) -> TextAnalysisResponse:
    """Analyzes message or communication text using the real SentryMesh V4 model.

    Privacy Guarantee: Text is processed in-memory only and never logged.
    """
    try:
        return analyze_text_content(
            text=payload.text,
            input_type=payload.input_type
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error during text analysis: {str(exc)}"
        )


@router.post("/call/transcript", response_model=TextAnalysisResponse)
def analyze_call_transcript_endpoint(payload: TextAnalysisRequest) -> TextAnalysisResponse:
    """Analyzes a suspicious call transcript using the real SentryMesh V4 model.

    Privacy Guarantee: Transcript is processed in-memory only and never logged.
    """
    try:
        # Enforce call_transcript vector type for this dedicated route
        return analyze_text_content(
            text=payload.text,
            input_type="call_transcript"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error during call transcript analysis: {str(exc)}"
        )
