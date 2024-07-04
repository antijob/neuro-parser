from server.apps.bot.models import Channel
from django.core.exceptions import ObjectDoesNotExist
from aiogram.types import Message
from typing import Optional

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
