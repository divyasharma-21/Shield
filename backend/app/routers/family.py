"""Family Circle sharing router."""

from fastapi import APIRouter
from app.schemas import FamilyShareRequest, FamilyShareResponse
from app.services.family_summary_service import create_family_share_summary

router = APIRouter(prefix="/api/v1/family", tags=["Family"])


@router.post("/share-summary", response_model=FamilyShareResponse)
def share_family_summary_endpoint(payload: FamilyShareRequest) -> FamilyShareResponse:
    """Generates a concise, non-alarmist family verification summary from actual model results.

    Does not invent caller facts and does not automatically send notifications.
    """
    return create_family_share_summary(payload)
