from typing import Optional

from server.apps.core.models import Article, Source
from server.core.fetcher.libs.proxy import ProxyManager

from .base_client import ClientBase
from .http_client import HttpClient


class ClientFactory:
    @staticmethod
    async def get_client(
        source: Optional[Source] = None, article: Optional[Article] = None
    ) -> ClientBase:
        if source.needs_proxy:
            settings = await ProxyManager.get_proxy()
            return HttpClient(
                proxy=settings["proxy_url"],
                login=settings["proxy_login"],
                password=settings["proxy_password"],
            )
        return HttpClient()
