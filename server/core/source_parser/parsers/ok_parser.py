from typing import Iterable
import re
from .base_parser import ParserBase


class OkParser(ParserBase):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return re.match(r"https://ok\.ru/", url)

    @classmethod
    def extract_urls(cls, url: str, document=None) -> Iterable[str]:
        for node in document.css("a.media-text_a"):
            news_page_link = "https://ok.ru" + node.attributes["href"]
            yield news_page_link
