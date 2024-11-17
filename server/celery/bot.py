import asyncio
import logging
import sys

from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter
from celery.signals import celeryd_init, worker_shutdown
from celery.utils.log import get_task_logger

from server.apps.bot.bot_instance import get_bot_instance
from server.apps.bot.keyboards.downvote_kb import downvote_keyboard

from .celery_app import app

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = get_task_logger(__name__)

bot = None


@celeryd_init.connect
def setup_bot_instance(**kwargs):
    global bot
    bot = get_bot_instance()
    logger.debug("Bot instance initialized")


@worker_shutdown.connect
def close_bot_instance(**kwargs):
    if bot and bot.session:
        asyncio.run(bot.session.close())
        logger.debug("Bot session closed")


class SendMessageTask(app.Task):
    queue = "bot"
    rate_limit = "0.5/s"
    autoretry_for = (TelegramRetryAfter,)
    max_retries = 5
    retry_backoff = 30
    retry_backoff_max = 600
    retry_jitter = False


@app.task(base=SendMessageTask)
def send_message_to_channel(msg: str, chat_id: int, inc_id: int = 0):
    global bot
    logger.info(
        f"Starting send_message_to_channel for chat_id: {chat_id}, inc_id: {inc_id}"
    )
    keyboard = None

    if bot is None:
        logger.warning("Bot instance is None, reinitializing...")
        setup_bot_instance()

    if inc_id != 0:
        try:
            keyboard = downvote_keyboard(inc_id)
        except Exception as e:
            logger.error(f"Can't make downvote_keyboard: {e}")
            return f"Failed to create keyboard: {e}"

    async def send_message():
        try:
            await bot.send_message(text=msg, chat_id=chat_id, reply_markup=keyboard)
            logger.info(f"Message sent to chat_id: {chat_id}")
        except TelegramForbiddenError:
            logger.error(
                "Bot can't acces the chat, please check it. Chat id: " + str(chat_id)
            )
            return "Bot can't acces the chat, please check it. Chat id: " + str(chat_id)
        except Exception as e:
            logger.error(f"Error sending message to channel: {e}")
            return f"Error sending message to channel: {e}"
        return "Message sent"

    try:
        loop = asyncio.get_event_loop()

        if loop.is_closed():
            logger.debug("Event loop is closed; creating a new event loop.")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            logger.info(
                "Running send_message in a running loop using run_coroutine_threadsafe"
            )
            result = asyncio.run_coroutine_threadsafe(send_message(), loop).result()
        else:
            logger.info("Running send_message using run_until_complete")
            result = loop.run_until_complete(send_message())

    except Exception as e:
        logger.error(f"Critical error in send_message_to_channel: {e}")
        raise

    return result
