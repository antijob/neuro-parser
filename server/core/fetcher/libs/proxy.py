from asgiref.sync import sync_to_async
from server.apps.core.models import Proxy
from random import choice


class ProxyManager:
    @staticmethod
    async def get_proxy() -> str:
        return choice(ProxyManager._get_proxies())

    @staticmethod
    async def _get_proxies() -> list[str]:
        proxies = sync_to_async(list)(Proxy.objects.all())
        return [f"{proxy.ip}:{proxy.port}" for proxy in proxies]
