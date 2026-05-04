from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ExtractorInput:
    url: str
    html: str


@dataclass(frozen=True, slots=True)
class ExtractedLink:
    href: str
    text: str | None = None


@dataclass(frozen=True, slots=True)
class ExtractorOutput:
    title: str | None = None
    text: str | None = None
    links: list[ExtractedLink] | None = None


class Extractor(Protocol):
    def extract(self, data: ExtractorInput) -> ExtractorOutput: ...

