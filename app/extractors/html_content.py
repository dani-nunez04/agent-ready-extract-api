from __future__ import annotations

from app.extractors.base import (
    ExtractedLink,
    Extractor,
    ExtractorInput,
    ExtractorOutput,
)
from app.schemas.extract import ExtractOptions
from app.utils.html import (
    extract_headings,
    extract_meta_description,
    extract_text,
    extract_title,
    iter_links,
    parse_html,
)


class HtmlContentExtractor(Extractor):
    """
    Generic HTML extractor (best-effort).

    MVP focuses on:
    - title
    - plain text
    - basic links (optional)
    """

    def extract(self, data: ExtractorInput) -> ExtractorOutput:
        # Default behavior if no options are provided at this layer.
        return self.extract_with_options(data, ExtractOptions())

    def extract_with_options(self, data: ExtractorInput, options: ExtractOptions) -> ExtractorOutput:
        soup = parse_html(data.html)

        title: str | None = extract_title(soup) if options.include_title else None
        description: str | None = extract_meta_description(soup)
        headings: list[str] | None = extract_headings(soup)
        text: str | None = extract_text(soup) if options.include_text else None

        links: list[ExtractedLink] | None = None
        if options.include_links:
            links = [ExtractedLink(href=href, text=txt) for (href, txt) in iter_links(soup, base_url=data.url)]

        return ExtractorOutput(title=title, description=description, headings=headings, text=text, links=links)

