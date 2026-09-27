"""Pydantic data schemas for SentryMesh Guardian API requests and responses.

Follows strict privacy, security, and response contracts.
"""

from typing import List, Dict, Optional, Any

from pydantic import BaseModel, Field, field_validator


class AnalyzeRequest(BaseModel):
    """Input payload for POST /analyze endpoint."""

    text: str = Field(
        ...,
        min_length=2,
        max_length=8000,
        description="The communication or message content to inspect.",
    )

    channel: str = Field(
        default="sms",
        description=(
            "Originating communication channel: "
            "sms | whatsapp | email | call | qr | website | app"
        ),
    )

    user_consent: bool = Field(
        default=True,
        description=(
            "Explicit user consent to analyze this content "
            "in-memory for security evaluation."
        ),
    )

    @field_validator("channel")
    @classmethod
    def validate_channel(cls, v: str) -> str:
        valid_channels = {
            "sms",
            "whatsapp",
            "email",
            "call",
            "qr",
            "website",
            "app",
        }

        clean = v.lower().strip()

        if clean not in valid_channels:
            return "sms"

        return clean


class ClassificationResult(BaseModel):
    """Predicted risk category and probability distribution."""

    predicted_label: str = Field(
        ...,
        description="Categorical prediction",
    )

    probabilities: Dict[str, float] = Field(
        ...,
        description="Calibrated probabilities per class",
    )


class ExtractedEntities(BaseModel):
    """Indicators of compromise and tokens parsed from input."""

    urls: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    emails: List[str] = Field(default_factory=list)
    phone_numbers: List[str] = Field(default_factory=list)
    upi_ids: List[str] = Field(default_factory=list)
    amounts: List[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    """Contract for POST /analyze output."""

    classification: ClassificationResult

    entities: ExtractedEntities

    tactics: Dict[str, float] = Field(
        ...,
        description="Scores for detected manipulation tactics (0.0 to 1.0)",
    )

    verification: Dict[str, Any] = Field(
        ...,
        description="Signals from URL/domain reputation and heuristics",
    )

    explanation: List[str] = Field(
        ...,
        description="Step-by-step evidence-based reasons explaining the evaluation",
    )

    recommended_actions: List[str] = Field(
        ...,
        description="Immediate concrete safety steps for the user",
    )

    uncertainty: str = Field(
        ...,
        description="low | medium | high uncertainty indicator",
    )


class WebGuardRequest(BaseModel):
    """Input payload for POST /webguard."""

    url: str = Field(
        ...,
        min_length=3,
        max_length=4096,
        description="URL to inspect for phishing and deceptive-site indicators.",
    )

    resolve_dns: bool = Field(
        default=True,
        description="Whether DNS resolution should be attempted for the hostname.",
    )

    reputation: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Optional externally supplied reputation signals. "
            "No external connection is initiated automatically."
        ),
    )

    # Optional PhiUSIIL-compatible webpage features.
    # These are supplied only when an upstream component already has
    # the corresponding observed webpage features.
    webpage_features: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Optional PhiUSIIL-compatible webpage feature vector for "
            "trained WebGuard ML analysis. Missing features are not "
            "fabricated by the API."
        ),
    )

    user_consent: bool = Field(
        default=True,
        description="Explicit user consent to evaluate the supplied URL.",
    )


class WebGuardResponse(BaseModel):
    """Structured WebGuard security assessment."""
    url: str
    normalized_url: Optional[str] = None
    valid_url: bool = True
    domain: Optional[str] = None
    risk_level: str
    risk_score: float
    signals: List[str] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    explainable_report: Dict[str, Any] = Field(default_factory=dict)
    recommended_actions: List[str] = Field(default_factory=list)
    note: str = ""


class AppGuardRequest(BaseModel):
    """Input payload for POST /appguard."""

    app_name: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Application name shown to the user.",
    )

    package_name: Optional[str] = Field(
        default=None,
        max_length=300,
        description="Application package/bundle identifier.",
    )

    publisher: Optional[str] = Field(
        default=None,
        max_length=300,
        description="Application publisher or developer.",
    )

    installation_source: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Source from which the application was installed.",
    )

    permissions: List[str] = Field(
        default_factory=list,
        description="Permissions requested or currently granted by the application.",
    )

    accessibility_enabled: bool = False
    screen_capture_enabled: bool = False
    overlay_enabled: bool = False
    sms_access_enabled: bool = False
    contacts_access_enabled: bool = False
    device_admin_enabled: bool = False

    reputation: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional externally supplied application reputation signals.",
    )

    user_consent: bool = Field(
        default=True,
        description="Explicit user consent to evaluate the supplied application metadata.",
    )


class AppGuardResponse(BaseModel):
    """Structured AppGuard application-risk assessment."""
    app_name: str
    package_name: Optional[str] = None
    publisher: Optional[str] = None
    installation_source: Optional[str] = None
    status: str = "analyzed"
    risk_level: str
    risk_score: Optional[float] = None
    signals: List[str] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)
    explainable_report: Dict[str, Any] = Field(default_factory=dict)
    recommended_actions: List[str] = Field(default_factory=list)
    note: str = ""


class ReportSubmission(BaseModel):
    """User-submitted feedback/threat report for quarantine buffer."""

    text: str = Field(
        ...,
        min_length=5,
        max_length=8000,
    )

    channel: str = "sms"

    suspected_label: Optional[str] = None

    user_notes: Optional[str] = None

    consent_anonymized_research: bool = False

    user_consent: bool = Field(
        default=False,
        description="Explicit consent to place the sanitized submission into the quarantine review workflow.",
    )
# Backward-compatible legacy ParentCall Guardian API contracts.
from typing import Literal
InputType = Literal['call_transcript','sms','whatsapp','email','payment_message','social_message']
PredictedLabel = Literal['suspicious','legitimate']
SafetyLevel = Literal['high_risk','suspicious_needs_verification','uncertain_needs_verification','no_strong_risk_signal']
class HealthResponse(BaseModel):
    status: str='ok'; model_loaded: bool=False; model_name: str='sentrymesh_messageguard_v5'; selected_suspicious_threshold: float=0.62; audio_transcription_configured: bool=False; voice_authenticity_configured: bool=False
class TextAnalysisRequest(BaseModel):
    text: str=Field(...,description='Message text or transcript to analyze'); input_type: InputType='call_transcript'
    @field_validator('text')
    @classmethod
    def validate_non_whitespace_length(cls,v):
        stripped=v.strip()
        if len(''.join(v.split()))<10: raise ValueError('Text must contain at least 10 non-whitespace characters.')
        return stripped
class EvidenceItem(BaseModel):
    feature: str; contribution: float
class ModelEvidence(BaseModel):
    signals_favoring_suspicious: List[EvidenceItem]=Field(default_factory=list); signals_favoring_legitimate: List[EvidenceItem]=Field(default_factory=list)
class ExplanationBlock(BaseModel):
    summary: str; evidence_summary: List[str]; uncertainty_note: str
class TextAnalysisResponse(BaseModel):
    module: str='parent_call_guardian'; status: str='analyzed'; predicted_label: PredictedLabel; suspicious_probability: float; selected_threshold: float; safety_level: SafetyLevel; input_type: InputType; model_evidence: ModelEvidence; explanation: ExplanationBlock; recommended_actions: List[str]; privacy_notice: str; disclaimer: str
class FamilyShareRequest(BaseModel):
    safety_level: SafetyLevel; suspicious_probability: float; evidence_summary: List[str]=Field(default_factory=list); recommended_actions: List[str]=Field(default_factory=list); disclaimer: Optional[str]=None
class FamilyShareResponse(BaseModel):
    title: str='SentryMesh Guardian Alert'; safety_level: SafetyLevel; safety_level_display: str; why_text: str; recommended_action_text: str; disclaimer_text: str; full_share_text: str
class AudioNotConfiguredResponse(BaseModel):
    module: str; status: str='not_configured'; message: str
class AudioAnalysisResponse(BaseModel):
    module: str='parent_call_audio'; status: str='analyzed'; transcription_analysis: Optional[TextAnalysisResponse]=None; voice_authenticity_analysis: Optional[dict]=None
