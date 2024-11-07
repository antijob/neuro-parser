from typing import Optional
from server.apps.core.models import Source, Article

from .base_client import ClientBase
from .http_client import HttpClient
from .telethon_client import TelethonClient


class ClientFactory:
    @staticmethod
    def get_client(
        source: Optional[Source] = None, article: Optional[Article] = None
    ) -> ClientBase:
        if source.is_tg_hidden:
            return TelethonClient()
        return HttpClient()
