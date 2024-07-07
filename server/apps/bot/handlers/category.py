import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from asgiref.sync import sync_to_async
from magic_filter import F

from server.apps.bot.data.messages import CATEGORIES_MESSAGE, COUNTRY_MESSAGE
from server.apps.bot.handlers.utils import chat_in_db
from server.apps.bot.keyboards.category_kb import (
    CategoryCallbackFactory,
    category_keyboard,
)
from server.apps.bot.keyboards.country_kb import country_keyboard
from server.apps.bot.models import ChannelIncidentType

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("categ"))
async def categ_command(message: Message) -> None:
    """
    Handle the /categ command.

    This function checks if the channel exists in the database and creates a keyboard
    with all categories. It then sends a message with the categories to the user.

    Args:
        message (Message): The incoming message object.

    Returns:
        None
    """

    current_chat = await chat_in_db(message)
    if not current_chat:
        return
    keyboard = await category_keyboard(current_chat)

    await message.answer(
        text=CATEGORIES_MESSAGE,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.callback_query(CategoryCallbackFactory.filter(F.action == "update"))
async def category_status_change_callback(
    callback: CallbackQuery, callback_data: CategoryCallbackFactory
):
    """
    Handle the callback for updating a category's status.

    This function toggles the status of a specific incident type for the current channel,
    then updates the keyboard to reflect the change.

    Args:
        callback (CallbackQuery): The callback query object.
        callback_data (CategoryCallbackFactory): The callback data containing incident type information.

    Returns:
        None
    """

    chn = await chat_in_db(callback.message)
    if not chn:
        return None

    cit = await sync_to_async(ChannelIncidentType.objects.get)(
        id__exact=int(callback_data.channel_incident_type_id)
    )
    cit.status = not cit.status
    await sync_to_async(cit.save)()

    keyboard = await category_keyboard(chn)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(CategoryCallbackFactory.filter(F.action == "config"))
async def category_config_callback(
    callback: CallbackQuery, callback_data: CategoryCallbackFactory
):
    chn = await chat_in_db(callback.message)
    if not chn:
        return

    keyboard = await country_keyboard(callback_data.channel_incident_type_id)
    await callback.message.edit_text(text=COUNTRY_MESSAGE, reply_markup=keyboard)
    await callback.answer()
