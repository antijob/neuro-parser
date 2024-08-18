from typing import Type, Optional
from server.apps.core.models import Source, Article

from client_interface import BaseClient
from client import NPClient


class ClientFactory:
    @staticmethod
    def get_client(
        source: Optional[Source], article: Optional[Article]
    ) -> Type[BaseClient]:
        return NPClient()
