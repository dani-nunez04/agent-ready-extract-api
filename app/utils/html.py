from __future__ import annotations

from typing import Iterable
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def parse_html(html: str) -> BeautifulSoup:
    # lxml parser is provided by the dependency `lxml`
    return BeautifulSoup(html, "lxml")


def extract_title(soup: BeautifulSoup) -> str | None:
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
        return title or None
    return None


def _remove_noise(soup: BeautifulSoup) -> None:
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()


def extract_text(soup: BeautifulSoup) -> str | None:
    _remove_noise(soup)
    text = soup.get_text(separator="\n")
    lines = [ln.strip() for ln in text.splitlines()]
    compact = "\n".join([ln for ln in lines if ln])
    return compact or None


def iter_links(soup: BeautifulSoup, base_url: str | None = None) -> Iterable[tuple[str, str | None]]:
    for a in soup.find_all("a"):
        href = (a.get("href") or "").strip()
        if not href:
            continue
        resolved = urljoin(base_url, href) if base_url else href
        text = a.get_text(strip=True) or None
        yield resolved, text

