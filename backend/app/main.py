"""FastAPI application entrypoint for SentryMesh Guardian.

Endpoints:
  - GET  /          : Health check and operational status
  - POST /analyze   : MessageGuard cognitive analysis
  - POST /webguard  : WebGuard URL/domain analysis
  - POST /appguard  : AppGuard application-risk analysis
  - POST /report    : Quarantined community threat reporting
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    AppGuardRequest,
    AppGuardResponse,
    ReportSubmission,
    WebGuardRequest,
    WebGuardResponse,
)

from app.analyzer import analyze_communication
from app.intelligence_reports import build_message_report, build_parent_report
from app.app_guard import analyze_app
from app.reporting import submit_user_report, get_quarantine_report
from app.web_guard import analyze_web_url
from app.routers import health, analysis as legacy_analysis, audio, family


app = FastAPI(
    title="SentryMesh Guardian API",
    description=(
        "Privacy-preserving AI Cybersecurity Defense System "
        "against scams, phishing, fraud calls, UPI fraud, "
        "risky websites, and risky applications."
    ),
    version="1.0.0",
)


# Enable CORS for local testing and web frontends.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Preserve the original backend API surface while the unified SentryMesh routes are added.
app.include_router(health.router)
app.include_router(legacy_analysis.router)
app.include_router(audio.router)
app.include_router(family.router)


@app.get("/", tags=["Health"])
def root_status():
    """Returns system status, active channels, and defense framework state."""

    return {
        "status": "operational",
        "service": "SentryMesh Guardian API",
        "version": "1.0.0",
        "framework": (
            "Observe -> Detect -> Analyse -> Explain -> "
            "Respond -> Learn"
        ),
        "channels_supported": [
            "sms",
            "whatsapp",
            "email",
            "call",
            "qr",
            "website",
            "app",
        ],
        "modules": [
            "MessageGuard",
            "WebGuard",
            "AppGuard",
            "ParentGuardian",
            "ReportGuard",
        ],
    }


@app.post(
    "/analyze",
    tags=["MessageGuard"],
)
def analyze_endpoint(payload: AnalyzeRequest):
    """Run the versioned MessageGuard ML pipeline with a complete explainable report."""
    if not payload.user_consent:
        raise HTTPException(status_code=400, detail="User consent is required to process communication content.")
    try:
        return build_message_report(payload.text, payload.channel)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"MessageGuard inference error: {exc}")


@app.post("/parentguardian", tags=["ParentGuardian"])
def parentguardian_endpoint(payload: AnalyzeRequest):
    """Run the dedicated safety-domain ParentGuardian model."""
    if not payload.user_consent:
        raise HTTPException(status_code=400, detail="User consent is required to process communication content.")
    try:
        return build_parent_report(payload.text, payload.channel)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"ParentGuardian inference error: {exc}")


@app.post(
    "/webguard",
    response_model=WebGuardResponse,
    tags=["WebGuard"],
)
def webguard_endpoint(payload: WebGuardRequest):
    """Analyze a URL for phishing and deceptive-site indicators."""

    if not payload.user_consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "User consent is required to evaluate "
                "the supplied URL."
            ),
        )

    try:
        result = analyze_web_url(
            url=payload.url,
            reputation=payload.reputation,
            resolve_dns=payload.resolve_dns,
            webpage_features=payload.webpage_features,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An error occurred while evaluating "
                f"the URL: {str(exc)}"
            ),
        )


@app.post(
    "/appguard",
    response_model=AppGuardResponse,
    tags=["AppGuard"],
)
def appguard_endpoint(payload: AppGuardRequest):
    """Analyze application metadata, permissions, and risk indicators."""

    if not payload.user_consent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "User consent is required to evaluate "
                "the supplied application."
            ),
        )

    try:
        result = analyze_app(
            app_name=payload.app_name,
            package_name=payload.package_name,
            publisher=payload.publisher,
            installation_source=payload.installation_source,
            permissions=payload.permissions,
            accessibility_enabled=payload.accessibility_enabled,
            screen_capture_enabled=payload.screen_capture_enabled,
            overlay_enabled=payload.overlay_enabled,
            sms_access_enabled=payload.sms_access_enabled,
            contacts_access_enabled=payload.contacts_access_enabled,
            device_admin_enabled=payload.device_admin_enabled,
            reputation=payload.reputation,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An error occurred while evaluating "
                f"the application: {str(exc)}"
            ),
        )


@app.get("/model-ops", tags=["Model Ops"])
def model_ops():
    """Expose real model metadata and evaluation artifacts without fabricating metrics."""
    import json
    from pathlib import Path
    base=Path(__file__).resolve().parent.parent
    reports=base/"reports"; models=base/"models"
    out=[]
    for p in sorted(reports.glob("*metrics.json")):
        try:
            d=json.loads(p.read_text(encoding="utf-8")); out.append({"artifact":p.name,"metrics":d})
        except Exception: pass
    return {"active_models":{
      "messageguard":"sentrymesh_messageguard_v5_word_char_logreg",
      "parentguardian":"parentguardian_safety_v1",
      "tactic_model":"sentrymesh_tactic_v2",
      "webguard":"webguard_phiusiil_logreg (when compatible features are supplied)",
      "appguard":"metadata discovery + transparent evidence analysis"
    },"artifacts":[p.name for p in models.glob("*.joblib")],"evaluation_reports":out,"honesty_note":"Metrics shown here are loaded from saved evaluation artifacts; no synthetic performance numbers are generated at runtime."}


@app.post(
    "/report",
    tags=["ReportGuard"],
)
def report_endpoint(payload: ReportSubmission):
    """Submit an anonymized threat report to the quarantine buffer."""

    if not payload.user_consent:
        raise HTTPException(status_code=400, detail="Explicit consent is required before a report is stored in quarantine.")

    try:
        result = submit_user_report(payload.model_dump())

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Failed to submit quarantine report: "
                f"{str(exc)}"
            ),
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

@app.get("/report/{report_id}", tags=["ReportGuard"])
def report_status_endpoint(report_id: str):
    """Return sanitized quarantine metadata for an authorized review workflow."""
    record = get_quarantine_report(report_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Quarantine report not found.")
    return {
        "report_id": record["report_id"],
        "timestamp": record["timestamp"],
        "status": record["status"],
        "channel": record["channel"],
        "sanitized_text": record["sanitized_text"],
        "sanitized_reviewer_note": record.get("sanitized_reviewer_note"),
        "sanitization": record["sanitization"],
        "training_ingestion": record["training_ingestion"],
        "retention_note": record.get("retention_note"),
    }
