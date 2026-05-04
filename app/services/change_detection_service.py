from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChangeDetectionResult:
    changed: bool
    previous_hash: str | None
    current_hash: str


class ChangeDetectionService:
    """
    v2 stub.

    TODO(v2): Persist previous hashes per URL (DB/kv store) and provide
    a proper API to compare the last known extracted content.
    """

    def __init__(self) -> None:
        pass

