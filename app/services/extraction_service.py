from __future__ import annotations

from datetime import UTC, datetime

from app.clients.http_client import HttpClient
from app.core.errors import ExtractionError, UpstreamFetchError
from app.extractors.base import ExtractorInput
from app.extractors.html_content import HtmlContentExtractor
from app.schemas.common import FetchMeta
from app.schemas.extract import ExtractOptions, ExtractResponse, ExtractResult, ExtractedLink


class ExtractionService:
    def __init__(
        self,
        *,
        http_client: HttpClient,
        extractor: HtmlContentExtractor | None = None,
    ) -> None:
        self._http = http_client
        self._extractor = extractor or HtmlContentExtractor()

    async def extract_from_url(self, *, url: str, options: ExtractOptions) -> ExtractResponse:
        fetched_at = datetime.now(UTC)

        try:
            fetched = await self._http.fetch(url)
        except UpstreamFetchError:
            # Re-raise as-is; API layer will map it to HTTP error later.
            raise

        # Best-effort decode; HTML is often messy. We'll refine in v2 if needed.
        try:
            html_text = fetched.content.decode("utf-8", errors="replace")
        except Exception as e:  # pragma: no cover
            raise ExtractionError(code="decode_failed", message=str(e)) from e

        try:
            out = self._extractor.extract_with_options(ExtractorInput(url=fetched.final_url, html=html_text), options)
        except Exception as e:
            raise ExtractionError(code="extract_failed", message=str(e)) from e

        links: list[ExtractedLink] | None = None
        if out.links is not None:
            links = [ExtractedLink(href=l.href, text=l.text) for l in out.links]

        fetch_meta = FetchMeta(
            fetched_at=fetched_at,
            final_url=fetched.final_url,
            status_code=fetched.status_code,
            content_type=fetched.content_type,
        )

        result = ExtractResult(
            title=out.title,
            description=out.description,
            headings=out.headings,
            text=out.text,
            links=links,
        )

        return ExtractResponse(url=str(url), fetch=fetch_meta, result=result)

