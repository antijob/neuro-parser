from typing import Iterable

from lxml import cssselect, etree
import re

from .base_parser import ParserBase


class TgParser(ParserBase):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return re.match(r"https://t\.me/", url)

    # Почему здесь дополнительный запрос ?
    @classmethod
    def extract_urls(cls, url: str, document=None) -> Iterable[str]:
        links = cssselect.CSSSelector("a.tgme_widget_message_date")(document)

        for link in links:
            yield link.get("href")
