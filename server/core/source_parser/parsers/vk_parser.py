from typing import Iterable

import re
from lxml import etree

from server.core.article_parser.parsers.base_parser import ParserBase


class VkParser(ParserBase):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return re.match(r"https://vk\.com/", url)

    @classmethod
    def extract_urls(cls, url: str, document=None) -> Iterable[str]:
        links = CSSSelector("a.PostHeaderSubtitle__link")(document)

        for link in links:
            news_page_link = "https://vk.com" + link.get("href")
            yield news_page_link
