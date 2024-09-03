from django.core.management.base import BaseCommand
from server.core.fetcher.clients.telethon_client import TelethonClient


class Command(BaseCommand):
    help = "Init TelethonClient connection"

    def handle(self, *args, **kwargs):
        client = TelethonClient()
        client.init_session()
