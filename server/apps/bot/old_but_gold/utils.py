from server.apps.bot.models import Channel
from django.core.exceptions import ObjectDoesNotExist

import logging
import inspect

logger = logging.getLogger(__name__)


def chat_in_db(chat_id, context):
    """
    Checks if chat_id in db
    If yes returns Channel object
    If no returns None and logs error
    """
    try:
        return Channel.objects.get(channel_id__exact=chat_id)
    except ObjectDoesNotExist:
        context.bot.send_message(
            chat_id=chat_id, text="Проверьте настройки бота, что-то пошло не так"
        )
        logger.error(
            f"Can't find channel {chat_id}, while executing __{inspect.stack()[1].function}__ function"
        )
        return None
