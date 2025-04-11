import logging
from typing import Any
from telethon import TelegramClient
import asyncio

from server.core.fetcher.libs.url_parser import get_telegram_ids

from server.apps.core.models import Article, Source

from .base_client import ClientBase
from server.settings.components.telethon import (
    TELEGRAM_API_HASH,
    TELEGRAM_API_ID,
)

from telethon.tl.types import PeerUser, PeerChat, PeerChannel


logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

TELETHON_LOCK: bool = False


class TelethonClient(ClientBase):
    session_name = ".telethon/telethon_session"

    def __init__(
        self, telegram_api_id=TELEGRAM_API_ID, telegram_api_hash=TELEGRAM_API_HASH
    ):
        self.client = TelegramClient(
            self.session_name, telegram_api_id, telegram_api_hash
        )
        logging.getLogger("telethon").setLevel(level=logging.CRITICAL)

    async def __aenter__(self):
        global TELETHON_LOCK
        while TELETHON_LOCK is True:
            await asyncio.sleep(1)
            logger.debug("TelethonClient: Can't lock, sleep")
        TELETHON_LOCK = True
        logger.exception("TelethonClient: Aquire lock")
        await self.client.connect()
        if not await self.client.is_user_authorized():
            logger.exception("TelethonClient: Release lock (not authorized)")
            TELETHON_LOCK = False
            raise Exception("User is not authorized")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        global TELETHON_LOCK
        await self.client.disconnect()
        logger.exception("TelethonClient: Release lock")
        TELETHON_LOCK = False

    async def get_article(self, article: Article, source: Source, articles_to_create: list[Article] = None) -> Article:
        """Fetch and process article content from Telegram."""
        logger.info(f"Getting article: {article.url}")

        try:
            ids = get_telegram_ids(article.url)
            if not ids.message_id:
                return article

            entity = await self.client.get_entity(PeerChannel(ids.channel_id))
            message = await self.client.get_messages(entity, ids=ids.message_id)

            if message:
                article.title = f"Message from {source.url}"
                article.text = message.message
                article.publication_date = message.date

        except Exception as e:
            logger.error(f"Error fetching Telegram message: {e}")

        return article

    async def get_source(self, source: Source) -> dict[str, Any]:
        ids = get_telegram_ids(source.url)

        res: dict[str, Any] = {}

        entity = ids.channel_id
        messages = await self.client.get_messages(entity, limit=10)
        for message in messages:
            url = f"{ids.base_url}{ids.channel_id}/{message.id}"
            res[url] = message

        return res

    async def init_session_async(self):
        await self.client.start()
        me = await self.client.get_me()
        print(f"Вы вошли как {me.username} ({me.id})")

    def init_session(self):
        with self.client as client:
            client.loop.run_until_complete(self.init_session_async())
