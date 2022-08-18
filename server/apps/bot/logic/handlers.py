from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from telegram import Update
from telegram.ext import CallbackContext

from server.apps.bot.logic.messages import (
    HELP_COMMAND_MESSAGE,
    MANUAL_INCIDENT_CREATION_MESSAGE_TEMPLATE,
    CATEGORIES_MESSAGE,
)
from server.apps.bot.logic.models import create_incident
from server.apps.bot.logic.parsers import (
    extract_text_and_url,
    incident_message_to_dict,
)


class UnknownError(Exception):
    pass


def help_callback(update, _context: CallbackContext) -> None:
    update.message.reply_text(
        text=HELP_COMMAND_MESSAGE, parse_mode="HTML", disable_web_page_preview=True
    )


def create_template_incident(update: Update, _context: CallbackContext) -> None:
    update.message.reply_text(
        "Скопируйте шаблон и начните заполнение."
    )
    update.message.reply_text(MANUAL_INCIDENT_CREATION_MESSAGE_TEMPLATE, parse_mode='HTML')


def categories_list(update: Update, _context: CallbackContext) -> None:
    update.message.reply_text(
        "Скопируйте шаблон и начните заполнение."
    )
    update.message.reply_text(CATEGORIES_MESSAGE, parse_mode='HTML')


def any_message_callback(update: Update, _context: CallbackContext):
    validate = URLValidator()

    if update.message and update.message.forward_from_chat:
        username = update.message.forward_from_chat.username
        message_id = update.message.forward_from_message_id
        description = update.message.text
        if not description and update.message.caption:
            description = update.message.caption

        message = f"https://t.me/{username}/{message_id}"
    else:
        description = None
        message = update.message.text.strip()

    if message.startswith("+"):
        try:
            return create_incident(update, **incident_message_to_dict(message))
        except UnknownError:
            return update.message.reply_text("Произошла неизвестная ошибка при ручном создании инцидента")

    if message.startswith(";") or message.startswith("@"):
        return

    if message.startswith("http"):
        create_incident(update, url=message, text=description)
    else:
        text, url = extract_text_and_url(message)

        if url and text:
            try:
                validate(url)
                create_incident(update, url=url, text=text)
            except ValidationError:
                update.message.reply_text(
                    "Ошибка при создании инцидента, некорректный URL-адрес."
                )
        else:
            update.message.reply_text("Не удалось создать инцидент.")
