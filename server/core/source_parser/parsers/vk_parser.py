from typing import Iterable
import re
from .base_parser import ParserBase


class VkParser(ParserBase):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return re.match(r"https://vk\.com/", url)

    @classmethod
    def extract_urls(cls, url: str, document=None) -> Iterable[str]:
        for node in document.css("a.PostHeaderSubtitle__link"):
            news_page_link = "https://vk.com" + node.attributes["href"]
            yield news_page_link
