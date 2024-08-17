import os
from typing import Optional
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from asgiref.sync import sync_to_async
import re


from server.apps.core.models import Article, Source


from server.core.fetcher.clients.client_interface import BaseClient


class TelethonClient(BaseClient):
    def __init__(self):
        # Fetch environment variables for the Telegram API
        self.api_id = int(os.getenv("TELEGRAM_API_ID", ""))
        self.api_hash = os.getenv("TELEGRAM_API_HASH", "")
        self.phone_number = os.getenv("TELEGRAM_PHONE_NUMBER", "")
        self.client = TelegramClient("session_name", self.api_id, self.api_hash)

    async def __aenter__(self):
        await self.client.connect()
        if not await self.client.is_user_authorized():
            await self.client.send_code_request(self.phone_number)
            try:
                code = os.getenv("TELEGRAM_LOGIN_CODE")
                await self.client.sign_in(self.phone_number, code)
            except SessionPasswordNeededError:
                password = os.getenv("TELEGRAM_PASSWORD")
                await self.client.sign_in(password=password)
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.client.disconnect()

    async def get_article(self, article: Article, source: Source) -> Article:
        """
        Fetches an article from Telegram by parsing its URL and populates
        the article's title, text, and publication date.
        """
        channel_regex = r"(?:https:\/\/t\.me\/)(?P<channel>\w+)\/(?P<message_id>\d+)"

        match = re.search(channel_regex, article.url)
        if match:
            channel = match.group("channel")
            message_id = match.group("message_id")

            # Fetch the message content from Telegram
            message = await self.client.get_messages(channel, ids=int(message_id))

            if message:
                # Update the article's fields based on the Telegram message
                article.title = f"Message from {channel}"
                article.text = message.message
                article.publication_date = message.date

                # Optionally, save the article if needed
                await sync_to_async(article.save, thread_sensitive=True)()

        return article

    async def get_source(self, source: Source) -> Optional[str]:
        """
        Fetches source details from Telegram based on the source's URL, which may refer
        to a channel or a user. Returns a description of the source (e.g., bio, channel description).
        """
        url = source.url
        channel_regex = r"(?:https:\/\/t\.me\/)(?P<channel>\w+)"
        user_regex = r"(?:https:\/\/t\.me\/)(?P<username>\w+)"

        if re.match(channel_regex, url):
            match = re.search(channel_regex, url)
            if match:
                channel = match.group("channel")
                # Fetch channel details
                entity = await self.client.get_entity(channel)
                if hasattr(entity, "about"):
                    return entity.about  # Channel description
                else:
                    return "No description available for this channel."

        elif re.match(user_regex, url):
            match = re.search(user_regex, url)
            if match:
                username = match.group("username")
                # Fetch user details
                entity = await self.client.get_entity(username)
                if hasattr(entity, "about"):
                    return entity.about  # User bio
                else:
                    return "No bio available for this user."

        return None
