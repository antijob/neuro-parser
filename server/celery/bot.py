import asyncio
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types.message import Message
from celery.signals import celeryd_init, worker_shutdown
from celery.utils.log import get_task_logger
from server.apps.bot.bot_instance import get_bot_instance
from .celery_app import app

logger = get_task_logger(__name__)

bot = None


@celeryd_init.connect
def setup_bot_instance(**kwargs):
    global bot
    bot = get_bot_instance()


@worker_shutdown.connect
def close_bot_instance(**kwargs):
    if bot and bot.session:
        asyncio.run(bot.session.close())


class SendMessageTask(app.Task):
    queue = "bot"
    rate_limit = "0.8/s"
    autoretry_for = (TelegramRetryAfter,)
    max_retries = 5
    retry_backoff = 30
    retry_backoff_max = 600
    retry_jitter = False


@app.task(base=SendMessageTask)
def send_message_to_channels(msg: str, chat_id: int):
    global bot
    if bot is None:
        setup_bot_instance()

    async def send_message():
        try:
            await bot.send_message(text=msg, chat_id=chat_id)
        except Exception as e:
            logger.error(f"Error sending message to channel: {e}")
            raise
        return "Message sent"

    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        result = loop.run_until_complete(send_message())
    except Exception as e:
        logger.error(f"Error in send_message_to_channels: {e}")
        raise

    return result