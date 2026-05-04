from fastapi import APIRouter

from app.api.v1.endpoints.extract import router as extract_router
from app.api.v1.endpoints.health import router as health_router

router = APIRouter()
router.include_router(health_router, tags=["health"])
router.include_router(extract_router, tags=["extract"])

