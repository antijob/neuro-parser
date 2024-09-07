from abc import ABC, abstractmethod
from typing import Iterable
from server.libs.handler import Handler


class ParserBase(Handler):
    @classmethod
    @abstractmethod
    def can_handle(cls, url: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def extract_urls(cls, url: str, document=None) -> Iterable[str]:
        pass
