from asgiref.sync import sync_to_async
from server.apps.core.models import Proxy
from random import choice

from asgiref.sync import sync_to_async


class ProxyManager:
    @staticmethod
    async def get_proxy() -> str:
        proxy = await sync_to_async(Proxy.objects.order_by("?").first)()
        return f"{proxy.ip}:{proxy.port}"
