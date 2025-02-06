from typing import Iterable
import re
from .base_parser import ParserBase, Source

from ..utils import build_document


class OkParser(ParserBase):
    @classmethod
    def can_handle(cls, source: Source) -> bool:
        return re.match(r"https://ok\.ru/", source.url)

    @classmethod
    def extract_urls(cls, source: Source, html: str) -> Iterable[str]:
        document = build_document(html)
        for node in document.css("a.media-text_a"):
            news_page_link = "https://ok.ru" + node.attributes["href"]
            yield news_page_link
