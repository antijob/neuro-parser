from abc import ABC, abstractmethod
from collections import namedtuple

ArticleData = namedtuple("ArticleData", "title text date final_url")


class ParserBase(ABC):
    @classmethod
    @abstractmethod
    def can_handle(cls, url: str) -> bool:
        pass

    @classmethod
    @abstractmethod
    def parse_raw_data(cls, url: str, data) -> ArticleData:
        pass
