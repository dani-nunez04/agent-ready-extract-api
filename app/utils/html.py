from __future__ import annotations

from typing import Iterable
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from app.utils.url import is_http_url, normalize_url


def parse_html(html: str) -> BeautifulSoup:
    # lxml parser is provided by the dependency `lxml`
    return BeautifulSoup(html, "lxml")


def extract_title(soup: BeautifulSoup) -> str | None:
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        return title or None
    return None


def extract_meta_description(soup: BeautifulSoup) -> str | None:
    tag = soup.find("meta", attrs={"name": "description"})
    if tag is None:
        # common variant: og:description (best-effort)
        tag = soup.find("meta", attrs={"property": "og:description"})
    if tag is None:
        return None
    content = (tag.get("content") or "").strip()
    return content or None


def extract_headings(soup: BeautifulSoup) -> list[str] | None:
    headings: list[str] = []
    for level in ("h1", "h2", "h3", "h4", "h5", "h6"):
        for h in soup.find_all(level):
            text = h.get_text(" ", strip=True)
            if text:
                headings.append(text)
    return headings or None


def _remove_noise(soup: BeautifulSoup) -> None:
    # Obvious non-content and UI noise.
    for tag in soup(
        [
            "script",
            "style",
            "noscript",
            "svg",
            "canvas",
            "iframe",
            "form",
            "input",
            "button",
            "select",
            "option",
        ]
    ):
        tag.decompose()

    # Common layout noise containers.
    for tag in soup(["nav", "header", "footer", "aside"]):
        tag.decompose()

    # Best-effort removal by common id/class keywords.
    noise_keywords = (
        "cookie",
        "consent",
        "banner",
        "modal",
        "popup",
        "subscribe",
        "newsletter",
        "breadcrumb",
        "breadcrumbs",
        "sidebar",
        "advert",
        "ads",
        "promo",
        "paywall",
        "login",
        "signup",
    )
    for el in soup.find_all(True):
        ident = " ".join(
            [
                str(el.get("id") or ""),
                " ".join(el.get("class") or []),
                str(el.get("role") or ""),
            ]
        ).lower()
        if ident and any(k in ident for k in noise_keywords):
            el.decompose()


def extract_text(soup: BeautifulSoup) -> str | None:
    _remove_noise(soup)
    text = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines()]
    # Remove super-short lines that are often chrome/navigation noise.
    lines = [ln for ln in lines if ln and len(ln) >= 2]
    compact = "\n".join(lines)
    return compact or None


def iter_links(soup: BeautifulSoup, base_url: str | None = None) -> Iterable[tuple[str, str | None]]:
    for a in soup.find_all("a"):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        if href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        resolved = urljoin(base_url, href) if base_url else href
        # Drop fragments and normalize scheme/host casing.
        try:
            resolved = normalize_url(resolved)
        except Exception:
            continue
        if not is_http_url(resolved):
            continue

        # Optional: drop obvious tracking query params without rewriting semantics too much.
        parts = urlsplit(resolved)
        if parts.query and ("utm_" in parts.query or "gclid=" in parts.query or "fbclid=" in parts.query):
            # Keep URL as-is for now (v1). We intentionally avoid aggressive rewriting.
            pass

        text = a.get_text(strip=True) or None
        yield resolved, text

