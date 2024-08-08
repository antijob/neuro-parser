import asyncio
import logging
import sys

from aiogram import Dispatcher

from server.apps.bot.bot_instance import bot, close_bot
from server.apps.bot.handlers import category, chat, country, region, service

# bot instance imported from separate file
dp = Dispatcher()


dp.include_router(service.router)
dp.include_router(category.router)
dp.include_router(chat.router)
dp.include_router(country.router)
dp.include_router(region.router)


async def main() -> None:
    try:
        await dp.start_polling(bot)
    finally:
        await close_bot()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())
