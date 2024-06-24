import logging

from telegram import Bot

from server.settings.components.telegram import TELEGRAM_BOT_TOKEN

logger = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_BOT_TOKEN)


def send_message(user_id, message):
    try:
        bot.send_message(chat_id=user_id, text=message)
    except Exception as e:
        logger.error(f"Error while sending message: {e}")
