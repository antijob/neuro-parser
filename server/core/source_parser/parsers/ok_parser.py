from typing import Iterable

from lxml import etree
import re

from server.core.article_parser.parsers.base_parser import ParserBase


class OkParser(ParserBase):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return re.match(r"https://ok\.ru/", url)

    @classmethod
    def extract_urls(cls, url: str, document=None) -> Iterable[str]:
        document = etree.HTML(html)

        links = CSSSelector("a.media-text_a")(document)
        for link in links:
            news_page_link = "https://ok.ru" + link.get("href")
            yield news_page_link
