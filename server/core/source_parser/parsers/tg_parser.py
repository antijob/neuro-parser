from typing import Iterable
import re
from .base_parser import ParserBase, Source

from ..utils import build_document


class TgParser(ParserBase):
    @classmethod
    def can_handle(cls, source: Source) -> bool:
        return re.match(r"https://t\.me/", source.url)

    @classmethod
    def extract_urls(cls, url: str, document: str) -> Iterable[str]:
        document = build_document(document)
        for node in document.css("a.tgme_widget_message_date"):
            yield node.attributes["href"]
