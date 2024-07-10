from server.apps.bot.models import Channel
from django.core.exceptions import ObjectDoesNotExist
from aiogram.types import CallbackQuery, Message
from typing import Optional, Any, Union, Callable
from functools import wraps

import logging
import inspect
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


async def chat_in_db(message: Message) -> Optional[Channel]:
    """
    Checks if chat_id in db
    If yes returns Channel object
    If no returns None and logs error
    """
    try:
        return await sync_to_async(Channel.objects.get)(
            channel_id__exact=message.chat.id
        )
    except ObjectDoesNotExist:
        await message.answer("Канал не найден в базе данных.", show_alert=True)
        logger.error(
            f"Can't find channel {message.chat.id}, while executing __{inspect.stack()[1].function}__ function"
        )
        return None


def check_channel(func: Callable) -> Callable:
    """
    Decorator for checking if chat eixtst in db before executing handlre
    If yes function is executed
    If no just returns None
    """

    @wraps(func)
    async def wrapper(
        event: Union[Message, CallbackQuery], *args: Any, **kwargs: Any
    ) -> Any:
        message = event if isinstance(event, Message) else event.message
        channel = await chat_in_db(message)
        if not channel:
            return None
        return await func(event, *args, channel=channel, **kwargs)

    return wrapper
