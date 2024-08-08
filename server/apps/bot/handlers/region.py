import asyncio
import logging

from aiogram import Router
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import CallbackQuery
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
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


@router.callback_query(RegionCF.filter(F.action.in_(["add_region", "del_region"])))
@check_channel
async def category_config_callback(
    callback: CallbackQuery, callback_data: RegionCF, channel: Channel
) -> None:
    """
    Handle callbacks for adding or deleting a region.
    Update the ChannelCountry object and refresh the region keyboard.
    """
    logger.info("Callback received with data: %s", callback_data)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            logger.info("Attempt %d for processing callback", attempt + 1)

            def handle_transactional_logic(callback_data: RegionCF):
                with transaction.atomic():
                    try:
                        channel_country = (
                            ChannelCountry.objects.select_for_update().get(
                                id=int(callback_data.channel_country_id)
                            )
                        )
                    except ObjectDoesNotExist:
                        logger.error(
                            f"ChannelCountry object not found: {callback_data}"
                        )

                    if callback_data.action == "add_region":
                        channel_country.add_region(callback_data.region_code)
                        logger.info("Added region: %s", callback_data.region_code)
                    elif callback_data.action == "del_region":
                        channel_country.del_region(callback_data.region_code)
                        logger.info("Deleted region: %s", callback_data.region_code)

                    return channel_country.id

            channel_country_id = await sync_to_async(
                handle_transactional_logic, thread_sensitive=True
            )(callback_data)

            keyboard = await region_keyboard(channel_country_id, callback_data.page)

            await callback.message.edit_reply_markup(reply_markup=keyboard)
            await callback.answer()
            logger.info("Callback processing completed successfully")
            break

        except TelegramRetryAfter as e:
            logger.warning(
                f"Telegram API retry after exception: {e.retry_after} seconds"
            )
            if attempt == max_retries - 1:
                logger.error(f"Max retries reached for Telegram API: {e}")
                await callback.answer(
                    "Извините, произошла ошибка. Попробуйте позже.", show_alert=True
                )
                return
            await asyncio.sleep(e.retry_after)
            logger.info(f"Retrying after {e.retry_after} seconds")

        except TelegramBadRequest as e:
            logger.error(f"Telegram API error: {e}")
            return

        except Exception as e:
            logger.error(f"Error while adding or deleting region: {e}")
            await callback.answer(
                "Произошла ошибка при обновлении региона.", show_alert=True
            )
            return


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
