from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    api_title: str = Field(default="agent-ready-extract-api", alias="API_TITLE")
    api_description: str = Field(
        default="API REST para extracción legítima de contenido público (MVP).",
        alias="API_DESCRIPTION",
    )
    api_version: str = Field(default="0.1.0", alias="API_VERSION")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    cors_allow_origins: list[str] = Field(default_factory=list, alias="CORS_ALLOW_ORIGINS")

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def _parse_cors_allow_origins(cls, v: Any) -> list[str]:
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            raw = v.strip()
            if not raw:
                return []
            if raw == "*":
                return ["*"]
            return [part.strip() for part in raw.split(",") if part.strip()]
        return [str(v).strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

