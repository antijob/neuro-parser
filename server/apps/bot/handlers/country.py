import logging

from aiogram import Router
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from magic_filter import F

from server.apps.bot.data.messages import CATEGORIES_MESSAGE, REGION_MESSAGE
from server.apps.bot.handlers.utils import check_channel
from server.apps.bot.keyboards.category_kb import category_keyboard
from server.apps.bot.keyboards.country_kb import CountryCF, country_keyboard
from server.apps.bot.keyboards.region_kb import region_keyboard
from server.apps.bot.models import Channel, ChannelCountry

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(CountryCF.filter(F.action == "update"))
@check_channel
async def category_config_callback(
    callback: CallbackQuery, callback_data: CountryCF, channel: Channel
) -> None:
    """
    Handle the callback for updating a country's status.
    Toggle the status of the selected country and update the keyboard.
    """
    try:
        channel_country = await sync_to_async(ChannelCountry.objects.get)(
            id=int(callback_data.channel_country_id)
        )
        channel_country.status = not channel_country.status
        await sync_to_async(channel_country.save)()
    except Exception as e:
        logger.error(f"Error while updating country status: {e}")
        return

    cit = await sync_to_async(lambda: channel_country.channel_incident_type)()
    keyboard = await country_keyboard(cit)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(CountryCF.filter(F.action == "back"))
@check_channel
async def back_to_category(callback: CallbackQuery, channel: Channel):
    """
    Handle the callback for returning to the category selection.
    Update the message with the category keyboard.
    """
    keyboard = await category_keyboard(channel)
    await callback.message.edit_text(text=CATEGORIES_MESSAGE, reply_markup=keyboard)


@router.callback_query(CountryCF.filter(F.action == "region"))
@check_channel
async def country_region_config(
    callback: CallbackQuery, callback_data: CountryCF, channel: Channel
):
    """
    Handle the callback for configuring a country's regions.
    Update the message with the region keyboard for the selected country.
    """
    keyboard = await region_keyboard(callback_data.channel_country_id)
    await callback.message.edit_text(text=REGION_MESSAGE, reply_markup=keyboard)
    await callback.answer()
