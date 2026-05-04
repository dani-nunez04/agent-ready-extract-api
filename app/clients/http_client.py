from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx

from app.core.errors import UpstreamFetchError


@dataclass(frozen=True, slots=True)
class FetchResult:
    final_url: str
    status_code: int
    content_type: str | None
    content: bytes


class HttpClient:
    """
    Conservative HTTP client for public pages.

    - No proxies, no fingerprint spoofing, no login automation.
    - Adds basic safety limits (timeouts, max bytes).
    """

    def __init__(
        self,
        *,
        timeout_s: float = 15.0,
        max_bytes: int = 2_000_000,
        max_redirects: int = 10,
        user_agent: str = "agent-ready-extract-api/0.1 (+https://example.invalid)",
    ) -> None:
        if timeout_s <= 0:
            raise ValueError("timeout_s must be > 0")
        if max_bytes <= 0:
            raise ValueError("max_bytes must be > 0")
        if max_redirects < 0:
            raise ValueError("max_redirects must be >= 0")

        self._timeout = httpx.Timeout(timeout_s)
        self._max_bytes = max_bytes
        self._max_redirects = max_redirects
        self._headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en,es;q=0.8",
        }

        self._client = httpx.AsyncClient(
            headers=self._headers,
            timeout=self._timeout,
            follow_redirects=True,
            max_redirects=self._max_redirects,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def fetch(self, url: str) -> FetchResult:
        try:
            resp = await self._client.get(url)
        except (httpx.InvalidURL, httpx.UnsupportedProtocol) as e:
            raise UpstreamFetchError(code="invalid_url", message=str(e)) from e
        except (httpx.TimeoutException, asyncio.TimeoutError) as e:
            raise UpstreamFetchError(code="timeout", message="Upstream request timed out") from e
        except httpx.HTTPError as e:
            raise UpstreamFetchError(code="http_error", message=str(e)) from e

        content = resp.content
        if len(content) > self._max_bytes:
            raise UpstreamFetchError(
                code="response_too_large",
                message=f"Response exceeded max_bytes={self._max_bytes}",
            )

        return FetchResult(
            final_url=str(resp.url),
            status_code=resp.status_code,
            content_type=resp.headers.get("content-type"),
            content=content,
        )

