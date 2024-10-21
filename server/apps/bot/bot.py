import asyncio
import logging
import sys

from aiogram import Dispatcher

from server.apps.bot.bot_instance import get_bot
from server.apps.bot.handlers import (
    category,
    chat,
    country,
    private,
    region,
    service,
    downvote,
)

# bot instance imported from separate file
dp = Dispatcher()


dp.include_router(private.router)
dp.include_router(service.router)
dp.include_router(category.router)
dp.include_router(chat.router)
dp.include_router(country.router)
dp.include_router(region.router)
dp.include_router(downvote.router)


async def main() -> None:
    async with get_bot() as bot:
        await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    asyncio.run(main())
