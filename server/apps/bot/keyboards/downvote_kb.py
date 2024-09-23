from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from server.apps.bot.data.settings import DOWNVOTE


class DownvoteCallbackFactory(CallbackData, prefix="dvote"):
    incident_type_id: int


def downvote_keyboard(incident_type_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=DOWNVOTE,
        callback_data=DownvoteCallbackFactory(incident_type_id=incident_type_id),
    )
    return builder.as_markup()
