import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from server.apps.bot.logic.messages import (
    CATEGORIES_MESSAGE,
    COUNTRY_MESSAGE,
    REGION_MESSAGE,
)
from server.apps.bot.models import Channel, CountryStatus, RegionStatus, TypeStatus
from server.apps.core.models import IncidentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CROSS = "\U0000274c"
CHECK = "\U00002705"
PAGE_SIZE = 20


def create_country_keyboard(chn: Channel):
    """
    Creates inline keyboard with all countries available in the database
    """
    logger.debug(f"create_country_keyboard: {chn}")
    try:
        countries = CountryStatus.objects.filter(channel=chn).order_by("id")
    except Exception as e:
        raise type(e)(f"create_country_keyboard exception happend: {e}")

    keyboard = list()

    for item in countries:
        btn_label = item.country.get_full_country_name()
        status = CHECK if item.status else CROSS

        keyboard.append(
            [
                InlineKeyboardButton(btn_label, callback_data=f"country_{item.id}"),
                InlineKeyboardButton(status, callback_data=f"country_{item.id}"),
            ]
        )

    return InlineKeyboardMarkup(keyboard)


def create_region_keyboard(chn: Channel, page: int = 0):
    """
    Creates inline keyboard with all regions available in the database
    regions divided into pages in size of page_size (20)
    """

    regions = RegionStatus.objects.filter(channel=chn).order_by("id")
    keyboard = list()
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    logger.debug(f"REGION_KEYBOARD: {start} {end}")

    for item in regions[start:end]:
        btn_label = item.region.get_full_region_name()
        status = CHECK if item.status else CROSS
        keyboard.append(
            [
                InlineKeyboardButton(
                    btn_label, callback_data=f"{page}_region_{item.id}"
                ),
                InlineKeyboardButton(status, callback_data=f"{page}_region_{item.id}"),
            ]
        )

    nav_buttons = []
    if start > 0:
        nav_buttons.append(
            InlineKeyboardButton("<", callback_data=f"{page}_region_back"),
        )
    if end < len(regions):
        nav_buttons.append(
            InlineKeyboardButton(">", callback_data=f"{page}_region_forward"),
        )
    keyboard.append(nav_buttons)

    return InlineKeyboardMarkup(keyboard)


def create_inline_keyboard(chn: Channel):
    """
    Creates inline keyboard for all types of incidents that we have in IncidentType model.
    """
    types = TypeStatus.objects.filter(channel=chn).order_by("id")
    keyboard = list()

    for item in types:
        btn_label = item.incident_type.description
        status = CHECK if item.status else CROSS

        keyboard.append(
            [
                InlineKeyboardButton(
                    btn_label, callback_data=f"categ_{item.incident_type.id}"
                ),
                InlineKeyboardButton(
                    status, callback_data=f"categ_{item.incident_type.id}"
                ),
            ]
        )

    return InlineKeyboardMarkup(keyboard)


def button_categ(update, context):
    """
    Callback function for pressing button on inline keyboard
    Each press cycle True and False values in dataclass
    and it changes text on buttons
    """
    query = update.callback_query
    query.answer()

    chn = Channel.objects.get(channel_id__exact=query.message.chat_id)

    button_data = query.data.partition("_")[2]
    incident_type = IncidentType.objects.get(id__exact=int(button_data))
    type_status = TypeStatus.objects.get(incident_type=incident_type, channel=chn)
    type_status.status = not type_status.status
    type_status.save()

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=CATEGORIES_MESSAGE,
        parse_mode="HTML",
        reply_markup=create_inline_keyboard(chn),
    )


def button_country(update, context):
    """
    Callback function for pressing button on inline country keyboard
    Each press cycle True and False values in dataclass
    and it changes text on buttons
    """
    query = update.callback_query
    query.answer()

    chn = Channel.objects.get(channel_id__exact=query.message.chat_id)

    # Extract the callback_data which contains the button information
    button_data = query.data.partition("_")[2]
    logger.debug(f"BUTTON_DATA: {button_data}")
    country = CountryStatus.objects.get(id__exact=int(button_data))
    country.status = not country.status
    country.save()

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=COUNTRY_MESSAGE,
        parse_mode="HTML",
        reply_markup=create_country_keyboard(chn),
    )


def button_region(update, context):
    """
    Callback function for pressing button on inline region keyboard
    Each press cycle True and False values in dataclass
    and it changes text on buttons
    """
    query = update.callback_query
    query.answer()

    chn = Channel.objects.get(channel_id__exact=query.message.chat_id)

    page = int(query.data.partition("_")[0])
    if "back" in query.data:
        page -= 1
    elif "forward" in query.data:
        page += 1
    else:
        button_data = query.data.rpartition("_")[2]
        region = RegionStatus.objects.get(id__exact=int(button_data))
        region.status = not region.status
        region.save()

    context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=REGION_MESSAGE,
        parse_mode="HTML",
        reply_markup=create_region_keyboard(chn, page),
    )
