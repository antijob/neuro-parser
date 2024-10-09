from typing import Tuple
from asgiref.sync import sync_to_async

from server.apps.core.models import Proxy
import aiohttp
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class ProxyManager:
    @staticmethod
    async def get_proxy() -> dict:
        proxy = await sync_to_async(
            Proxy.objects.filter(is_active=True).order_by("?").first
        )()
        # TODO enable proxy checking somehow
        # await ProxyManager().check_proxy(f"{proxy.ip}:{proxy.port}")
        return {
            "proxy_url": f"{proxy.ip}:{proxy.port}",
            "proxy_login": proxy.login,
            "proxy_password": proxy.password,
        }

    async def check_proxy(self, proxy: str) -> bool:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    "https://google.com", proxy=proxy, timeout=60
                ) as response:
                    if response.ok:
                        return True
                    else:
                        return False
            except Exception as e:
                logger.error(f"Proxy {proxy} check error: {e}")
