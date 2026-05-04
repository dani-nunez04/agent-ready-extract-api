from __future__ import annotations

import re
from typing import Iterable
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from app.utils.url import is_http_url, normalize_url


def parse_html(html: str) -> BeautifulSoup:
    # lxml parser is provided by the dependency `lxml`
    return BeautifulSoup(html, "lxml")


def _clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _meta_content(soup: BeautifulSoup, *, name: str | None = None, prop: str | None = None) -> str | None:
    attrs: dict[str, str] = {}
    if name is not None:
        attrs["name"] = name
    if prop is not None:
        attrs["property"] = prop
    tag = soup.find("meta", attrs=attrs) if attrs else None
    if tag is None:
        return None
    content = _clean_text(str(tag.get("content") or ""))
    return content or None


def extract_title(soup: BeautifulSoup) -> str | None:
    # Prefer social/meta titles when present (often cleaner).
    for candidate in (
        _meta_content(soup, prop="og:title"),
        _meta_content(soup, name="twitter:title"),
    ):
        if candidate:
            return candidate

    if soup.title and soup.title.string:
        title = _clean_text(soup.title.string)
        if title:
            return title

    h1 = soup.find("h1")
    if h1:
        text = _clean_text(h1.get_text(" ", strip=True))
        return text or None

    return None


def extract_meta_description(soup: BeautifulSoup) -> str | None:
    for candidate in (
        _meta_content(soup, name="description"),
        _meta_content(soup, prop="og:description"),
        _meta_content(soup, name="twitter:description"),
    ):
        if candidate:
            return candidate
    return None


def extract_headings(soup: BeautifulSoup) -> list[str] | None:
    headings: list[str] = []
    for level in ("h1", "h2", "h3", "h4", "h5", "h6"):
        for h in soup.find_all(level):
            text = _clean_text(h.get_text(" ", strip=True))
            if text and text not in headings:
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


def _select_main_container(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Pick the best-effort content container for text extraction.
    """
    for selector in ("main", "article"):
        node = soup.find(selector)
        if node is not None:
            return node

    # Heuristic: pick the largest <section> by text length.
    best = None
    best_len = 0
    for node in soup.find_all("section"):
        t = node.get_text(" ", strip=True)
        l = len(t)
        if l > best_len:
            best = node
            best_len = l
    if best is not None and best_len >= 200:
        return best

    return soup.body or soup


def extract_text(soup: BeautifulSoup) -> str | None:
    _remove_noise(soup)
    container = _select_main_container(soup)
    text = container.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines()]

    # Remove super-short lines and obvious boilerplate fragments.
    drop_exact = {
        "accept all",
        "reject all",
        "cookie policy",
        "privacy policy",
        "terms of service",
        "sign in",
        "log in",
    }
    cleaned: list[str] = []
    for ln in lines:
        if not ln:
            continue
        if len(ln) < 2:
            continue
        low = ln.lower()
        if low in drop_exact:
            continue
        if re.fullmatch(r"[|•·\-–—\s]+", ln):
            continue
        cleaned.append(ln)

    # De-duplicate consecutive lines (common with sticky headers/menus).
    deduped: list[str] = []
    prev = None
    for ln in cleaned:
        if ln == prev:
            continue
        deduped.append(ln)
        prev = ln

    compact = "\n".join(deduped)
    return compact or None


def iter_links(soup: BeautifulSoup, base_url: str | None = None) -> Iterable[tuple[str, str | None]]:
    seen: set[str] = set()
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
        if resolved in seen:
            continue
        seen.add(resolved)

        # Optional: drop obvious tracking query params without rewriting semantics too much.
        parts = urlsplit(resolved)
        if parts.query and ("utm_" in parts.query or "gclid=" in parts.query or "fbclid=" in parts.query):
            # Keep URL as-is for now (v1). We intentionally avoid aggressive rewriting.
            pass

        text = _clean_text(a.get_text(" ", strip=True)) or None
        yield resolved, text

