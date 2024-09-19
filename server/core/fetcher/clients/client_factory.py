from typing import Optional

from server.apps.core.models import Article, Source
from server.core.fetcher.libs.proxy import ProxyManager

from .base_client import ClientBase
from .http_client import HttpClient


class ClientFactory:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @staticmethod
    async def get_client(
        source: Optional[Source] = None, article: Optional[Article] = None
    ) -> ClientBase:
        if source.needs_proxy:
            return HttpClient(proxy=ProxyManager.get_proxy())
        return HttpClient()
