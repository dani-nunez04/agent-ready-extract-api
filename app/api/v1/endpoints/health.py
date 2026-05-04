from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import APIStatus

router = APIRouter()


@router.get("/health", response_model=APIStatus, summary="Health check")
def health() -> APIStatus:
    settings = get_settings()
    return APIStatus(status="ok", version=settings.api_version)

