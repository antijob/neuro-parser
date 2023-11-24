from telegram import Update
from telegram.ext import CallbackContext

from server.apps.bot.logic.messages import (
    HELP_COMMAND_MESSAGE,
    CATEGORIES_MESSAGE,
    ADD_MESSAGE,
)
from server.apps.bot.logic.keyboard import create_inline_keyboard
from server.apps.bot.models import Channel
from server.apps.bot.models import TypeStatus
from server.apps.core.incident_types import IncidentType
from server.settings.components.telegram import TELEGRAM_BOT_NAME


def help_callback(update, _context: CallbackContext) -> None:
    update.message.reply_text(
        text=HELP_COMMAND_MESSAGE, parse_mode="HTML", disable_web_page_preview=True
    )


def new_chat_members(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    list_new_chat_members = update.message.new_chat_members

    message = f'Бот добавлен в чат - {update.message.chat.title}.' + ADD_MESSAGE

    for member in list_new_chat_members:
        if member.username == TELEGRAM_BOT_NAME and member.is_bot == True:
            try:
                chn = Channel.objects.create(channel_id=chat_id)
            except Exception as e:
                raise type(e)(
                    f'When you try create new chanell with {chat_id} exception happend: ' + e)

            for it in IncidentType.objects.all():
                type_status = TypeStatus.objects.create(
                    incident_type=it,
                    channel=chn,
                    status=True,
                )
            update.message.reply_text(message)


def categ(update, context):
    chat_id = update.message.chat_id

    try:
        # check if this chanel exist in db
        cats = Channel.objects.get(channel_id__exact=chat_id)
    except Exception as e:
        context.bot.send_message(
            chat_id=chat_id,
            text="Проверьте настройки бота, что-то пошло не так"
        )
        raise type(e)(
            f'When add bot to chat {chat_id} exception happend: ' + e)

    # Create and send the inline keyboard
    keyboard = create_inline_keyboard(cats)

    context.bot.send_message(
        chat_id=chat_id,
        text=CATEGORIES_MESSAGE,
        parse_mode='HTML',
        reply_markup=keyboard
    )


def chat_member_left(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    try:
        channel = Channel.objects.get(channel_id=chat_id)
        channel.delete()
    except Exception as e:
        raise type(e)(
            f'When remove bot from chat {chat_id} exception happend: ' + e)
