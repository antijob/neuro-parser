from typing import Iterable
import re
from .base_parser import ParserBase, Source
from ..utils import build_document


class VkParser(ParserBase):
    @classmethod
    def can_handle(cls, source: Source) -> bool:
        return re.match(r"https://vk\.com/", source.url)

    @classmethod
    def extract_urls(cls, url: str, document=None) -> Iterable[str]:
        document = build_document(document)
        for node in document.css("a.PostHeaderSubtitle__link"):
            news_page_link = "https://vk.com" + node.attributes["href"]
            yield news_page_link
