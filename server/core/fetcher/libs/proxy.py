from server.apps.core.models import Proxy
from random import choice


class ProxyManager:
    @staticmethod
    def get_proxy() -> str:
        return choice(ProxyF._get_proxies())

    @staticmethod
    def _get_proxies() -> list[str]:
        return [f"{proxy.ip}:{proxy.port}" for proxy in Proxy.objects.all()]
