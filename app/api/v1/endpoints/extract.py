from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.clients.http_client import HttpClient
from app.core.errors import ExtractionError, UpstreamFetchError
from app.schemas.common import ErrorResponse
from app.schemas.extract import ExtractRequest, ExtractResponse
from app.services.extraction_service import ExtractionService

router = APIRouter()


async def get_http_client() -> HttpClient:
    client = HttpClient()
    try:
        yield client
    finally:
        await client.aclose()


@router.post(
    "/extract",
    response_model=ExtractResponse,
    summary="Extract clean content from a public URL",
    description="Fetch a public web page and extract basic metadata and clean text. No logins, no CAPTCHAs, no proxies.",
    operation_id="extractFromUrl",
    responses={
        400: {"model": ErrorResponse},
        422: {"description": "Validation error"},
        502: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def extract(
    payload: ExtractRequest,
    http_client: HttpClient = Depends(get_http_client),
) -> ExtractResponse:
    service = ExtractionService(http_client=http_client)
    try:
        return await service.extract_from_url(url=str(payload.url), options=payload.options)
    except UpstreamFetchError as e:
        http_status = status.HTTP_400_BAD_REQUEST if e.code == "invalid_url" else status.HTTP_502_BAD_GATEWAY
        body = ErrorResponse(error=e.code, message=e.message).model_dump()
        return JSONResponse(status_code=http_status, content=body)
    except ExtractionError as e:
        body = ErrorResponse(error=e.code, message=e.message).model_dump()
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=body)

