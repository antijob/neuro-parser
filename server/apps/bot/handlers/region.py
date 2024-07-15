import logging

from aiogram import Router
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from magic_filter import F

from server.apps.bot.data.messages import (
    COUNTRY_MESSAGE,
)
from server.apps.bot.handlers.utils import check_channel
from server.apps.bot.keyboards.country_kb import country_keyboard
from server.apps.bot.keyboards.region_kb import RegionCF, region_keyboard
from server.apps.bot.models import Channel, ChannelCountry

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(RegionCF.filter(F.action == "add_region"))
@router.callback_query(RegionCF.filter(F.action == "del_region"))
@check_channel
async def category_config_callback(
    callback: CallbackQuery, callback_data: RegionCF, channel: Channel
) -> None:
    """
    Handle callbacks for adding or deleting a region.
    Update the ChannelCountry object and refresh the region keyboard.
    """
    try:
        channel_country = await sync_to_async(ChannelCountry.objects.get)(
            id=int(callback_data.channel_country_id)
        )
        if callback_data.action == "add_region":
            await sync_to_async(channel_country.add_region)(callback_data.region_code)
        if callback_data.action == "del_region":
            await sync_to_async(channel_country.del_region)(callback_data.region_code)
    except Exception as e:
        logger.error(f"Error while adding or deleting reigion: {e}")
        return

    keyboard = await region_keyboard(channel_country.id, callback_data.page)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(RegionCF.filter(F.action == "page_back"))
@router.callback_query(RegionCF.filter(F.action == "page_forward"))
@check_channel
async def change_page(
    callback: CallbackQuery, callback_data: RegionCF, channel: Channel
):
    """
    Handle callbacks for changing the page of the region keyboard.
    Update the keyboard with the new page.
    """
    if callback_data.action == "page_back":
        page = callback_data.page - 1
    elif callback_data.action == "page_forward":
        page = callback_data.page + 1
    else:
        page = callback_data.page

    keyboard = await region_keyboard(callback_data.channel_country_id, page=page)
    await callback.message.edit_reply_markup(reply_markup=keyboard)


@router.callback_query(RegionCF.filter(F.action == "back"))
@check_channel
async def back_to_category(
    callback: CallbackQuery, callback_data: RegionCF, channel: Channel
):
    """
    Handle the callback for returning to the country selection.
    Update the message with the country keyboard for the related channel incident type.
    """
    try:
        channel_country = await sync_to_async(
            lambda: ChannelCountry.objects.select_related("channel_incident_type").get(
                id=callback_data.channel_country_id
            )
        )()
        cit_id = channel_country.channel_incident_type.id
    except ChannelCountry.DoesNotExist:
        logger.error(
            f"Channel country with id {callback_data.channel_country_id} not found"
        )
        return

    keyboard = await country_keyboard(cit_id)
    await callback.message.edit_text(text=COUNTRY_MESSAGE, reply_markup=keyboard)
