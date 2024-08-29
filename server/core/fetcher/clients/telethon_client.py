import logging
from typing import Optional
from telethon import TelegramClient
from asgiref.sync import sync_to_async
import re
import asyncio

from server.apps.core.models import Article, Source

from .base_client import ClientBase
from server.settings.components.telethon import (
    TELEGRAM_API_HASH,
    TELEGRAM_API_ID,
)

from telethon.tl.types import PeerUser, PeerChat, PeerChannel


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class TelethonClient(ClientBase):
    session_name = "telethon_session"
    _lock = asyncio.Lock()

    def __init__(
        self, telegram_api_id=TELEGRAM_API_ID, telegram_api_hash=TELEGRAM_API_HASH
    ):
        self.client = TelegramClient(
            self.session_name, telegram_api_id, telegram_api_hash
        )
        logging.getLogger("telethon").setLevel(level=logging.CRITICAL)

    async def __aenter__(self):
        await self._lock.acquire()
        await self.client.connect()
        if not await self.client.is_user_authorized():
            self._lock.release()
            raise Exception("User is not authorized")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.client.disconnect()
        self._lock.release()

    @staticmethod
    def get_ids(url: str) -> list:
        pattern_message = (
            r"(?P<baseurl>https:\/\/[^\/]+\/(?:c\/)?)(?P<channel>\d+)\/(?P<message>\d+)"
        )
        pattern_channel = r"(?P<baseurl>https:\/\/[^\/]+\/(c\/)?)(?P<channel>[^\/]+)"

        match = re.match(pattern_message, url)
        if match:
            base_url = match.group("baseurl")
            channel = match.group("channel")
            message = match.group("message")

            if channel.isdigit():
                channel = int(channel)
            if message.isdigit():
                message = int(message)

            return [base_url, channel, message]

        match = re.match(pattern_channel, url)
        if match:
            base_url = match.group("baseurl")
            # is_hidden = match.group("is_hidden")
            channel = match.group("channel")

            if channel.isdigit():
                channel = int(channel)

            return [base_url, channel]

        return []

    async def get_article(self, article: Article, source: Source) -> Article:
        ids = self.get_ids(article.url)

        if ids and len(ids) == 3:
            entity = await self.client.get_entity(PeerChannel(ids[1]))
            message = await self.client.get_messages(entity, ids=ids[2])

            if message:
                article.title = f"Message from {source.url}"
                article.text = message.message
                article.publication_date = message.date

                await sync_to_async(article.save, thread_sensitive=True)()

        return article

    async def get_source(self, source: Source) -> Optional[str]:
        ids = self.get_ids(source.url)

        res = []

        if ids and len(ids) >= 1:
            if isinstance(ids[1], int):
                entity = await self.client.get_entity(PeerChannel(ids[1]))
            else:
                entity = ids[1]

            async for message in self.client.iter_messages(entity, limit=10):
                url = f"{ids[0]}{ids[1]}/{message.id}"
                res.append(url)
            return res

        # elif re.match(user_regex, url):
        #     match = re.search(user_regex, url)
        #     if match:
        #         username = match.group("username")
        #         # Fetch user details
        #         entity = await self.client.get_entity(username)
        #         if hasattr(entity, "about"):
        #             return entity.about  # User bio
        #         else:
        #             return None

        # return None

    async def init_session_async(self):
        await self.client.start()
        me = await self.client.get_me()
        print(f"Вы вошли как {me.username} ({me.id})")

    def init_session(self):
        with self.client as client:
            client.loop.run_until_complete(self.init_session_async())
