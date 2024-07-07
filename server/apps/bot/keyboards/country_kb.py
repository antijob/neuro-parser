import logging
from enum import Enum
from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from server.apps.bot.data.settings import CHECK, CROSS, REGIONS
from server.apps.bot.models import (
    ChannelCountry,
    ChannelIncidentType,
)

logger = logging.getLogger(__name__)


class Action(str, Enum):
    update = "update"
    region = "region"
    back = "back"


class CountryCF(CallbackData, prefix="cnt"):
    action: Action
    channel_country_id: Optional[int]


@sync_to_async
def country_keyboard(cit: ChannelIncidentType) -> Optional[InlineKeyboardMarkup]:
    try:
        countries = ChannelCountry.objects.filter(channel_incident_type=cit).order_by(
            "id"
        )
    except Exception as e:
        logger.error(f"Error creating country keyboard: {e}")
        return None

    builder = InlineKeyboardBuilder()

    for ch_country in countries:
        btn_label = ch_country.country.get_full_country_name()
        status = CHECK if ch_country.status else CROSS
        ch_country_id = ch_country.id

        builder.row(
            InlineKeyboardButton(
                text=btn_label,
                callback_data=CountryCF(
                    action=Action.update, channel_country_id=ch_country_id
                ).pack(),
            ),
            InlineKeyboardButton(
                text=status,
                callback_data=CountryCF(
                    action=Action.update, channel_country_id=ch_country_id
                ).pack(),
            ),
        )
        if ch_country.country.has_region():
            builder.row(
                InlineKeyboardButton(
                    text=REGIONS,
                    callback_data=CountryCF(
                        action=Action.region, channel_country_id=ch_country_id
                    ).pack(),
                )
            )

    back_button = InlineKeyboardButton(
        text="<< Назад",
        callback_data=CountryCF(action=Action.back, channel_country_id=None).pack(),
    )
    keyboard = builder.as_markup()
    keyboard.inline_keyboard.append([back_button])

    return keyboard
