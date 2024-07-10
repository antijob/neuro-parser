from typing import Iterable
import re
from .base_parser import ParserBase


class TgParser(ParserBase):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return re.match(r"https://t\.me/", url)

    @classmethod
    def extract_urls(cls, url: str, document=None) -> Iterable[str]:
        for node in document.css("a.tgme_widget_message_date"):
            yield node.attributes["href"]
