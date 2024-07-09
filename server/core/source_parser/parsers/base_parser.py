from abc import ABC, abstractmethod
from typing import Iterable


class ParserBase(ABC):
    @classmethod
    @abstractmethod
    def can_handle(cls, url: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def extract_urls(cls, url: str, document=None) -> Iterable[str]:
        pass
