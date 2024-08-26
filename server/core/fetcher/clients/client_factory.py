from typing import Optional
from server.apps.core.models import Source, Article

from base_client import BaseClient
from client import NPClient


class ClientFactory:
    @staticmethod
    def get_client(
        source: Optional[Source] = None, article: Optional[Article] = None
    ) -> BaseClient:
        return NPClient()
