import logging
from enum import Enum
from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async

from server.apps.bot.data.settings import CHECK, CROSS, PAGE_SIZE
from server.apps.bot.models import (
    ChannelCountry,
)
from server.apps.core.models import Region

logger = logging.getLogger(__name__)


class Action(str, Enum):
    add_region = "add_region"
    del_region = "del_region"
    back = "back"
    page_back = "page_back"
    page_forward = "page_forward"


class RegionCF(CallbackData, prefix="reg"):
    action: Action
    page: int = 0
    channel_country_id: Optional[int]
    region_code: Optional[str] = None


@sync_to_async
def region_keyboard(
    ch_country_id: int, page: int = 0
) -> Optional[InlineKeyboardMarkup]:

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    # Filter regions to show by current country
    try:
        channel_country = ChannelCountry.objects.select_related("country").get(
            id=ch_country_id
        )
        country = channel_country.country
    except ChannelCountry.DoesNotExist:
        logger.error(f"Can't get country for channel_country_id: {ch_country_id}")
        return None

    all_regions = Region.objects.filter(country=country).exclude(name="ALL")

    # Taking only regions from start to end
    number_of_regions = len(all_regions)
    regions_to_show = all_regions[start:end]

    # Get the list of enabled regions
    try:
        enabled_regions: list[str] = ChannelCountry.objects.get(
            id=ch_country_id
        ).enabled_regions
    except Exception as e:
        logger.error(f"Can't get enabled regions: {e}")
        return None

    builder = InlineKeyboardBuilder()

    for r in regions_to_show:
        if r.name in enabled_regions:
            btn_label = f"{CHECK} {r.get_full_region_name()}"
            btn_action = Action.del_region
        else:
            btn_label = f"{CROSS} {r.get_full_region_name()}"
            btn_action = Action.add_region
        builder.button(
            text=btn_label,
            callback_data=RegionCF(
                action=btn_action,
                page=page,
                channel_country_id=ch_country_id,
                region_code=r.name,
            ),
        )
    builder.adjust(1)
    keyboard = builder.as_markup()

    nav_buttons = []

    logger.debug(f"start: {start} end: {end} len: {len(enabled_regions)}")
    if start > 0:
        back_page = InlineKeyboardButton(
            text="<",
            page=page - 1,
            callback_data=RegionCF(
                action=Action.page_back, channel_country_id=ch_country_id, page=page
            ).pack(),
        )
        nav_buttons.append(back_page)
    if end < number_of_regions:
        forward_page = InlineKeyboardButton(
            text=">",
            page=page + 1,
            callback_data=RegionCF(
                action=Action.page_forward, channel_country_id=ch_country_id, page=page
            ).pack(),
        )
        nav_buttons.append(forward_page)
    keyboard.inline_keyboard.append(nav_buttons)

    back_button = InlineKeyboardButton(
        text="<< К странам",
        callback_data=RegionCF(
            action=Action.back, channel_country_id=ch_country_id
        ).pack(),
    )
    keyboard.inline_keyboard.append([back_button])

    return keyboard
