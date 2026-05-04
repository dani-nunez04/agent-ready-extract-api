from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit


def is_http_url(url: str) -> bool:
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    return parts.scheme in {"http", "https"} and bool(parts.netloc)


def normalize_url(url: str) -> str:
    """
    Normalize a URL for consistent downstream processing.

    - Lowercases scheme + hostname
    - Drops fragment
    - Keeps query/path as-is (do not rewrite semantics)
    """
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    fragment = ""
    return urlunsplit((scheme, netloc, parts.path, parts.query, fragment))

