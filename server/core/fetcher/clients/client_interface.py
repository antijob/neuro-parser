from abc import ABC, abstractmethod
from typing import Optional


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
    async def get(self, url: str) -> tuple[str, str]:
        pass

    @abstractmethod
    async def get_article(self, article, source) -> object:
        pass

    @abstractmethod
    async def get_source(self, source) -> Optional[str]:
        pass
