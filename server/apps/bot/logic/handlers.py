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
    REGION_MESSAGE,
    HELP_COMMAND_MESSAGE,
)
from server.apps.bot.models import Channel, TypeStatus, CountryStatus, RegionStatus
from server.apps.core.models import Country, Region, IncidentType
from server.settings.components.telegram import TELEGRAM_BOT_NAME


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
                chn = Channel.objects.create(channel_id=chat_id)
            except Exception as e:
                raise type(e)(
                    f"Error in add bot in chat {chat_id} exception happend: {e}"
                )

            for incident in IncidentType.objects.all():
                TypeStatus.objects.create(
                    incident_type=incident,
                    channel=chn,
                    status=True,
                )
            for country in Country.objects.all():
                CountryStatus.objects.create(
                    country=country,
                    channel=chn,
                    status=True,
                )
            for region in Region.objects.all():
                RegionStatus.objects.create(
                    region=region,
                    channel=chn,
                    status=True,
                )

            update.message.reply_text(message)


def categ(update, context):
    """callback for /categ command"""

    chat_id = update.message.chat_id

    # check if this chanel exist in db
    try:
        cats = Channel.objects.get(channel_id__exact=chat_id)
    except Exception as e:
        context.bot.send_message(
            chat_id=chat_id, text="Проверьте настройки бота, что-то пошло не так"
        )
        raise type(e)(f"Category command in chat {chat_id} exception happend: {e}")

    if IncidentType.objects.exists():
        """Check if IncidentTypes exists"""
        for incident in IncidentType.objects.all():
            status = TypeStatus.objects.filter(
                incident_type=incident,
                channel=cats,
            )
            if not status:
                TypeStatus.objects.create(
                    incident_type=incident,
                    channel=cats,
                    status=True,
                )
    else:
        context.bot.send_message(
            chat_id=chat_id, text="Нет доступных типов инцидентов, нужно их добавить."
        )
        return

    keyboard = create_inline_keyboard(cats)

    context.bot.send_message(
        chat_id=chat_id,
        text=CATEGORIES_MESSAGE,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


def country(update, context):
    """callback for /country command"""

    chat_id = update.message.chat_id
    try:
        # check if this chanel exist in db
        cats = Channel.objects.get(channel_id__exact=chat_id)
    except Exception as e:
        context.bot.send_message(
            chat_id=chat_id, text="Проверьте настройки бота, что-то пошло не так"
        )
        raise type(e)(f"Country command in chat {chat_id} exception happend: {e}")

    keyboard = create_country_keyboard(cats)

    context.bot.send_message(
        chat_id=chat_id,
        text=COUNTRY_MESSAGE,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


def region(update, context):
    """callback for /region command"""

    chat_id = update.message.chat_id

    try:
        # check if this chanel exist in db
        cats = Channel.objects.get(channel_id__exact=chat_id)
    except Exception as e:
        context.bot.send_message(
            chat_id=chat_id, text="Проверьте настройки бота, что-то пошло не так"
        )
        raise type(e)(f"Country command in chat {chat_id} exception happend: {e}")

    keyboard = create_region_keyboard(cats)

    context.bot.send_message(
        chat_id=chat_id,
        text=REGION_MESSAGE,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


def chat_member_left(update: Update, context: CallbackContext):
    """
    on bot delete from chat delete also records from db
    """
    chat_id = update.message.chat_id
    try:
        channel = Channel.objects.get(channel_id=chat_id)
        channel.delete()
    except Exception as e:
        raise type(e)(f"When remove bot from chat {chat_id} exception happend: {e}")
