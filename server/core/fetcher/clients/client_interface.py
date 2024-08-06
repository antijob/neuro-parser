from abc import ABC, abstractmethod
from typing import Optional
from server.apps.core.models import Article, Source


class BaseClient(ABC):
    @abstractmethod
    async def __aenter__(self):
        """Async context manager entry."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback):
        """Async context manager exit."""
        pass

    @abstractmethod
    async def get_article(self, article: Article, source: Source) -> Article:
        pass

    @abstractmethod
    async def get_source(self, source: Source) -> Optional[str]:
        pass
