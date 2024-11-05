from abc import ABC, abstractmethod
from typing import Iterable, Union
from server.libs.handler import Handler

from server.apps.core.models import Article, Source


class ParserBase(Handler):
    @classmethod
    @abstractmethod
    def can_handle(cls, source: Source) -> bool:
        pass

    @classmethod
    @abstractmethod
    def extract_urls(cls, url: str, document: str) -> Iterable[Union[str, Article]]:
        pass
