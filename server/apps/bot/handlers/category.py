import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from asgiref.sync import sync_to_async
from magic_filter import F

from server.apps.bot.data.messages import CATEGORIES_MESSAGE, COUNTRY_MESSAGE
from server.apps.bot.handlers.utils import check_channel
from server.apps.bot.keyboards.category_kb import (
    CategoryCallbackFactory,
    category_keyboard,
)
from server.apps.bot.keyboards.country_kb import country_keyboard
from server.apps.bot.models import Channel, ChannelIncidentType

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("categ"))
@check_channel
async def categ_command(message: Message, channel: Channel) -> None:
    """
    Handle the /categ command.
    Display the categories message with the category keyboard.
    """
    keyboard = await category_keyboard(channel)
    await message.answer(
        text=CATEGORIES_MESSAGE,
        parse_mode="HTML",
        reply_markup=keyboard,
    )


@router.callback_query(CategoryCallbackFactory.filter(F.action == "update"))
@check_channel
async def category_status_change_callback(
    callback: CallbackQuery, callback_data: CategoryCallbackFactory, channel: Channel
):
    """
    Handle the callback for updating a category's status.
    Toggle the status of the selected category and update the keyboard.
    """
    cit = await sync_to_async(ChannelIncidentType.objects.get)(
        id__exact=int(callback_data.channel_incident_type_id)
    )
    cit.status = not cit.status
    await sync_to_async(cit.save)()

    keyboard = await category_keyboard(channel)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(CategoryCallbackFactory.filter(F.action == "config"))
@check_channel
async def category_config_callback(
    callback: CallbackQuery, callback_data: CategoryCallbackFactory, channel: Channel
):
    """
    Handle the callback for configuring a category.
    Update the message with the country keyboard for the selected category.
    """
    keyboard = await country_keyboard(callback_data.channel_incident_type_id)
    await callback.message.edit_text(text=COUNTRY_MESSAGE, reply_markup=keyboard)
    await callback.answer()
