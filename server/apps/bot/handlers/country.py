import logging

from aiogram import Router
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from magic_filter import F

from server.apps.bot.data.messages import CATEGORIES_MESSAGE
from server.apps.bot.handlers.utils import chat_in_db
from server.apps.bot.keyboards.category_kb import category_keyboard
from server.apps.bot.keyboards.country_kb import CountryCF, country_keyboard
from server.apps.bot.models import ChannelCountry

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(CountryCF.filter(F.action == "update"))
async def category_config_callback(
    callback: CallbackQuery, callback_data: CountryCF
) -> None:
    logger.info(f"Started country update: {callback_data}")
    chn = await chat_in_db(callback.message)
    if not chn:
        logger.warning("Channel not found")
        return

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
async def back_to_category(callback: CallbackQuery):
    chn = await chat_in_db(callback.message)
    if not chn:
        return None

    keyboard = await category_keyboard(chn)
    await callback.message.edit_text(text=CATEGORIES_MESSAGE, reply_markup=keyboard)
