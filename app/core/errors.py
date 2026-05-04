from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppError(Exception):
    """
    Base error for domain/application failures.

    Keep this independent from FastAPI/HTTP so it can be reused in services.
    """

    code: str
    message: str

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.code}: {self.message}"


@dataclass(frozen=True, slots=True)
class InvalidInputError(AppError):
    """Raised when user-provided input is invalid at the domain level."""


@dataclass(frozen=True, slots=True)
class UpstreamFetchError(AppError):
    """Raised when fetching an upstream URL fails (network/timeout/invalid response)."""


@dataclass(frozen=True, slots=True)
class ExtractionError(AppError):
    """Raised when HTML parsing/extraction fails in a non-recoverable way."""

