"""Audio upload, transcription, and authenticity management service.

Respects strict privacy guarantees:
- Audio processed in temporary files and securely deleted immediately.
- Never intercepts or records calls in background.
- If transcription or voice-authenticity models are not configured,
  reports not_configured without fabricating fake transcripts or deepfake scores.
"""

from pathlib import Path
import os
import tempfile
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status

from app.config import settings
from app.services.inference_service import analyze_text_content
from app.schemas import TextAnalysisResponse

SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".webm"}


class AudioService:
    def __init__(self):
        self.transcription_configured = settings.enable_audio_transcription
        self.authenticity_configured = settings.enable_voice_authenticity
        self._whisper_model = None

    def validate_file(self, file: UploadFile) -> str:
        """Validates file extension and filename safety."""
        filename = file.filename or "recording.wav"
        ext = Path(filename).suffix.lower()
        if ext not in SUPPORTED_AUDIO_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Unsupported audio format '{ext}'. Supported formats: "
                    f"{', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))}"
                )
            )
        return ext

    async def process_audio_upload(
        self,
        file: UploadFile
    ) -> Tuple[Optional[TextAnalysisResponse], Optional[dict]]:
        """Processes audio through optional speech-to-text and optional voice authenticity models.

        Uses temporary file storage with guaranteed cleanup in a try-finally block.
        """
        # Validate format
        ext = self.validate_file(file)

        # Check configuration
        if not self.transcription_configured:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail={
                    "module": "parent_call_audio",
                    "status": "not_configured",
                    "message": (
                        "Audio transcription requires a configured speech-to-text model. "
                        "No transcript-risk result has been generated."
                    )
                }
            )

        # Save to temporary file with byte size enforcement
        temp_file = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        temp_path = Path(temp_file.name)
        bytes_read = 0

        try:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                bytes_read += len(chunk)
                if bytes_read > settings.max_audio_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=(
                            f"File size exceeds the {settings.max_audio_file_mb}MB limit."
                        )
                    )
                temp_file.write(chunk)
            temp_file.flush()
            temp_file.close()

            # Execute transcription via faster-whisper if configured
            transcript_text = self._transcribe_audio(temp_path)

            # Analyze transcript using existing real V4 text model
            text_analysis = analyze_text_content(
                text=transcript_text,
                input_type="call_transcript"
            )

            # Separate voice authenticity path
            if self.authenticity_configured:
                voice_auth = self._evaluate_voice_authenticity(temp_path)
            else:
                voice_auth = {
                    "module": "voice_authenticity",
                    "status": "not_configured",
                    "message": (
                        "Voice authenticity analysis requires a configured and evaluated "
                        "anti-spoofing model. No deepfake result has been generated."
                    )
                }

            return text_analysis, voice_auth

        finally:
            # Guarantee deletion of temporary audio file
            if temp_path.exists():
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass

    def _transcribe_audio(self, audio_path: Path) -> str:
        """Transcribes audio using faster-whisper if installed."""
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail={
                    "module": "parent_call_audio",
                    "status": "not_configured",
                    "message": (
                        "faster-whisper package is not installed. "
                        "Please install requirements-optional.txt to enable local transcription."
                    )
                }
            )

        if self._whisper_model is None:
            self._whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

        segments, _ = self._whisper_model.transcribe(str(audio_path))
        text = " ".join([segment.text for segment in segments]).strip()
        if len("".join(text.split())) < 10:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Transcribed audio yielded fewer than 10 non-whitespace characters."
            )
        return text

    def _evaluate_voice_authenticity(self, audio_path: Path) -> dict:
        """Stub for future calibrated anti-spoof model (kept cleanly separate)."""
        return {
            "module": "voice_authenticity",
            "status": "not_configured",
            "message": "Voice authenticity model is not yet configured with trained weights."
        }


audio_service = AudioService()
