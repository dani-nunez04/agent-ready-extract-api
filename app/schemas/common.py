from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class APIStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str = Field(default="ok", description="High-level status string.")
    version: str = Field(..., description="API version.")


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: str = Field(..., description="Stable error code.")
    message: str = Field(..., description="Human-readable error message.")


class FetchMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fetched_at: datetime = Field(..., description="UTC timestamp when the URL was fetched.")
    final_url: str = Field(..., description="Final URL after redirects (if any).")
    status_code: int = Field(..., ge=100, le=599, description="HTTP status code returned by the upstream.")
    content_type: str | None = Field(default=None, description="Upstream Content-Type header (if present).")

