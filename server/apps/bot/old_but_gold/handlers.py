import logging

from django.core.exceptions import ObjectDoesNotExist
from telegram import Update
from telegram.ext import CallbackContext

from server.apps.bot.logic.keyboard import (
    create_country_keyboard,
    create_inline_keyboard,
    create_region_keyboard,
)
from server.apps.bot.logic.messages import (
    ADD_MESSAGE,
    CATEGORIES_MESSAGE,
    COUNTRY_MESSAGE,
    HELP_COMMAND_MESSAGE,
    REGION_MESSAGE,
)
from server.apps.bot.logic.utils import chat_in_db
from server.apps.bot.models import (
    Channel,
    ChannelCountry,
    ChannelIncidentType,
    CountryStatus,
    RegionStatus,
    TypeStatus,
)
from server.apps.core.incident_types import IncidentType
from server.apps.core.models import Country, Region
from server.settings.components.telegram import TELEGRAM_BOT_NAME

logger = logging.getLogger(__name__)


def help_callback(update, _context: CallbackContext) -> None:
    """callback for /help command"""
    update.message.reply_text(
        text=HELP_COMMAND_MESSAGE, parse_mode="HTML", disable_web_page_preview=True
    )


def new_chat_members(update: Update, context: CallbackContext):
    """
    on add to chat send welcome message and create
    status objects for all IncidentTypes, Country and Region
    """
    chat_id = update.message.chat_id
    list_new_chat_members = update.message.new_chat_members

    message = f"Бот добавлен в чат - {update.message.chat.title}. {ADD_MESSAGE}"

    for member in list_new_chat_members:
        if member.username == TELEGRAM_BOT_NAME and member.is_bot:
            try:
                Channel.objects.create(channel_id=chat_id)
            except Exception as e:
                raise type(e)(
                    f"Error in add bot in chat {chat_id} exception happend: {e}"
                )

            update.message.reply_text(message)


def categ(update, context):
    """
    Callback for /categ command. Check if channel exist in db
    and create keyboard with all categories
    """
    # TODO: если нужна проверка на то что типы инцедентов существуют, вынести ее отдельно
    # пока удалил
    # Создание опций если их нет, тоже удалил, если канал есть в базе,
    # то и свяазанные опции, должны были быть созданы при его добавлении

    chat_id = update.message.chat_id
    current_chat = chat_in_db(chat_id, context)
    if not current_chat:
        return
    keyboard = create_inline_keyboard(current_chat)

    context.bot.send_message(
        chat_id=chat_id,
        text=CATEGORIES_MESSAGE,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


def country(update, context):
    """
    Callback for /country command
    Check if chat exist in db
    and creates keyboard with all countries
    """

    chat_id = update.message.chat_id
    current_chat = chat_in_db(chat_id, context)
    if not current_chat:
        return
    keyboard = create_country_keyboard(current_chat)

    context.bot.send_message(
        chat_id=chat_id,
        text=COUNTRY_MESSAGE,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


# def region(update, context):
#     """callback for /region command"""
#
#     chat_id = update.message.chat_id
#
#     try:
#         # check if this chanel exist in db
#         cats = Channel.objects.get(channel_id__exact=chat_id)
#     except Exception as e:
#         context.bot.send_message(
#             chat_id=chat_id, text="Проверьте настройки бота, что-то пошло не так"
#         )
#         raise type(e)(f"Country command in chat {chat_id} exception happend: {e}")
#
#     keyboard = create_region_keyboard(cats)
#
#     context.bot.send_message(
#         chat_id=chat_id,
#         text=REGION_MESSAGE,
#         parse_mode="HTML",
#         reply_markup=keyboard,
#     )


def chat_member_left(update: Update, context: CallbackContext):
    """
    on bot delete from chat delete also records from db
    """
    # TODO: check if this all works

    chat_id = update.message.chat_id
    try:
        channel = Channel.objects.get(channel_id=chat_id)
        channel.delete()
    except Exception as e:
        raise type(e)(f"When remove bot from chat {chat_id} exception happend: {e}")
