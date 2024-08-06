from contextlib import asynccontextmanager

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from server.settings.components.telegram import TELEGRAM_BOT_TOKEN as TOKEN


@asynccontextmanager
async def get_bot():
    bot = Bot(token=str(TOKEN), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    try:
        yield bot
    finally:
        await bot.session.close()
