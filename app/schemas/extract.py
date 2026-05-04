from __future__ import annotations

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from app.schemas.common import FetchMeta


class ExtractOptions(BaseModel):
    """
    Request options for extraction.

    MVP: keep this small and safe; we'll extend in later phases.
    """

    model_config = ConfigDict(extra="forbid")

    include_text: bool = Field(default=True, description="Include extracted plain text (best-effort).")
    include_title: bool = Field(default=True, description="Include page title (best-effort).")
    include_links: bool = Field(default=False, description="Include outbound links (best-effort).")


class ExtractRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: AnyHttpUrl = Field(..., description="Public HTTP/HTTPS URL to fetch and analyze.")
    options: ExtractOptions = Field(default_factory=ExtractOptions)


class ExtractedLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    href: str = Field(..., description="Resolved or raw link target.")
    text: str | None = Field(default=None, description="Anchor text (if present).")


class ExtractResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, description="Best-effort document title.")
    text: str | None = Field(default=None, description="Best-effort main text.")
    links: list[ExtractedLink] | None = Field(default=None, description="Best-effort extracted links.")


class ExtractResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str = Field(..., description="Input URL as string.")
    fetch: FetchMeta | None = Field(default=None, description="Fetch metadata (present when fetch succeeded).")
    result: ExtractResult | None = Field(default=None, description="Extraction output (present when extraction succeeded).")

