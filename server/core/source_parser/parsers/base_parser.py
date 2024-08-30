from abc import ABC, abstractmethod
from typing import Iterable, Union

from server.apps.core.models import Article, Source


class ParserBase(ABC):
    @classmethod
    @abstractmethod
    def can_handle(cls, source: Source) -> bool:
        pass

    @classmethod
    @abstractmethod
    def extract_urls(cls, url: str, document=None) -> Union[str, Article]:
        pass
