import logging
from typing import Optional, Union

from server.apps.core.models import Article, Source
from server.core.fetcher.libs.proxy import ProxyManager

from .http_client import HttpClient
from .telethon_client import TelethonClient
from .http_proxy import HttpProxyClient

logger = logging.getLogger("parser")


class ClientFactory:
    @staticmethod
    async def get_client(
        source: Source, article: Optional[Article] = None
    ) -> Union[HttpClient, HttpProxyClient, TelethonClient]:
        if source.is_tg_hidden:
            logger.debug(f"Creating client for Telegram hidden source: {source}")
            return TelethonClient()
        if not source.needs_proxy:
            logger.debug(f"Creating client without proxy for source: {source}")
            return HttpClient()

        try:
            proxy_data = await ProxyManager.get_proxy()
            logger.info(
                f"Got proxy for source {source}: valid={proxy_data.is_valid}"
                f"{f', error={proxy_data.error_msg}' if not proxy_data.is_valid else ''}"
            )
        except Exception as e:
            logger.error(f"Error getting proxy for source {source}: {str(e)}")
            proxy_data = None

        # Create client with appropriate settings
        client = HttpProxyClient(proxy_data=proxy_data, use_proxy=True)

        return client
