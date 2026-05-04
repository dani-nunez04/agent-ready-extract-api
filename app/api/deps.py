from __future__ import annotations

import logging
import secrets

from fastapi import Header, HTTPException, status

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def verify_rapidapi_proxy_secret(
    x_rapidapi_proxy_secret: str | None = Header(
        default=None,
        alias="X-RapidAPI-Proxy-Secret",
        description=(
            "Shared secret added by RapidAPI's gateway/proxy. "
            "Direct calls to protected endpoints must include this header."
        ),
    ),
) -> None:
    """Fail-closed validation for calls that must come through RapidAPI.

    Returns 403 if:
    - RAPIDAPI_PROXY_SECRET is not configured, or
    - the header is missing, or
    - the header does not match.

    The response detail is intentionally generic to avoid leaking configuration.
    """

    settings = get_settings()
    expected = (settings.rapidapi_proxy_secret or "").strip()

    if not expected:
        logger.error("RAPIDAPI_PROXY_SECRET is not configured; denying access.")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    provided = x_rapidapi_proxy_secret
    if provided is None or not secrets.compare_digest(provided, expected):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
