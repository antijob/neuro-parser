import logging
from typing import Optional

from server.apps.core.models import Article, Source
from server.core.fetcher.libs.proxy import ProxyData, ProxyManager

from .http_client import HttpClient

logger = logging.getLogger("parser")


class ClientFactory:
    @staticmethod
    async def get_client(
        source: Source, article: Optional[Article] = None
    ) -> HttpClient:
        if source.needs_proxy:
            settings: ProxyData = await ProxyManager.get_proxy()
            if settings.is_valid:
                return HttpClient(
                    proxy=settings.url,
                    login=settings.login,
                    password=settings.password,
                )
            logger.error(settings.error_msg)
        return HttpClient()
