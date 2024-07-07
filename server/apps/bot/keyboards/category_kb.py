from enum import Enum

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from server.apps.bot.data.settings import CHECK, CROSS, SETTINGS
from server.apps.bot.models import Channel, ChannelIncidentType


### Dataclases buttons in category keyboard
class Action(str, Enum):
    update = "update"
    config = "config"


class CategoryCallbackFactory(CallbackData, prefix="cat"):
    action: Action
    channel_incident_type_id: int


@sync_to_async
def category_keyboard(chn: Channel) -> InlineKeyboardMarkup:
    """
    Creates inline keyboard for all types of incidents that we have in IncidentType model.
    """
    types = ChannelIncidentType.objects.filter(channel=chn).order_by("id")
    builder = InlineKeyboardBuilder()

    for item in types:
        btn_label = item.incident_type.description
        status = CHECK if item.status else CROSS

        builder.button(
            text=btn_label,
            callback_data=CategoryCallbackFactory(
                action=Action.update, channel_incident_type_id=item.id
            ),
        )
        builder.button(
            text=status,
            callback_data=CategoryCallbackFactory(
                action=Action.update, channel_incident_type_id=item.id
            ),
        )
        builder.button(
            text=SETTINGS,
            callback_data=CategoryCallbackFactory(
                action=Action.config, channel_incident_type_id=item.id
            ),
        )

    builder.adjust(3)
    return builder.as_markup()
