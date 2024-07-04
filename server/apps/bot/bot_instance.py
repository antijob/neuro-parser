from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from server.settings.components.telegram import TELEGRAM_BOT_TOKEN as TOKEN


def get_bot():
    """
    We create bot instance with default properties here
    so we can import it in different modules
    """
    return Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def close_bot():
    await bot.session.close()


bot = get_bot()
