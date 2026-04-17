from abc import abstractmethod
from typing import Iterable, Union

from server.apps.core.models import Article, Source
from server.libs.handler import Handler


class ParserBase(Handler):
    @classmethod
    @abstractmethod
    def can_handle(cls, source: Source) -> bool:
        pass

    @classmethod
    @abstractmethod
    def extract_urls(
        cls, source: Source, document: str
    ) -> Iterable[Union[str, Article]]:
        pass
