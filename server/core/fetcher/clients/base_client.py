from abc import ABC, abstractmethod
from typing import Union, Any

from server.apps.core.models import Source, Article

# ClientSourceData may be raw html data, list of urls, list of built Articles, dict of urls and relevant data or None
ClientSourceData = Union[str, list[str], list[Article], dict[str, Any], None]


class ClientBase(ABC):
    @abstractmethod
    async def __aenter__(self):
        """Async context manager entry."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback):
        """Async context manager exit."""
        pass

    @abstractmethod
    async def get_article(self, article: Article, source: Source, articles_to_create: list[Article] = None) -> Article:
        """
        Fetches an article and parses it into an Article object.
        May return a new Article object, for example, in case of a redirect
        """
        pass

    @abstractmethod
    async def get_source(self, source: Source) -> ClientSourceData:
        """
        Fetches raw data from the source.
        """
        pass
