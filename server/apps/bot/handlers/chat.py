import logging

from aiogram import Bot, Router
from aiogram.filters.chat_member_updated import (
    JOIN_TRANSITION,
    LEAVE_TRANSITION,
    ChatMemberUpdatedFilter,
)
from aiogram.types import ChatMemberUpdated
from asgiref.sync import sync_to_async

from server.apps.bot.data.messages import ADD_MESSAGE
from server.apps.bot.models import Channel
from server.apps.bot.services.country import create_settings

logger = logging.getLogger(__name__)

router = Router()


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def new_chat_member(event: ChatMemberUpdated, bot: Bot):
    """
    on add to chat send welcome message and create
    new channel object with all possible settings turned on
    """
    if event.new_chat_member.user.id != bot.id:
        return
    try:
        channel = await sync_to_async(Channel.objects.create)(channel_id=event.chat.id)
        logger.debug(f"Channel added: {channel}")
        await sync_to_async(create_settings)(channel)
    except Exception as e:
        logger.error(
            f"Error in add bot in chat {event.chat.title} with id: {event.chat.id} exception happend: {e}"
        )

    await event.answer(f"Бот добавлен в чат - {event.chat.title}. {ADD_MESSAGE}")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def left_chat_member(event: ChatMemberUpdated, bot: Bot):
    """
    On left the chat delete chat object frrom database
    """

    logger.info(
        f"Left chat member event triggered. Bot ID: {bot.id}, Left member ID: {event.old_chat_member.user.id}"
    )

    if event.old_chat_member.user.id != bot.id:
        return
    try:

        @sync_to_async
        def delete_channel():
            Channel.objects.filter(channel_id=event.chat.id).delete()

        await delete_channel()
        logger.info("Left chat member event completed.")
    except Exception as e:
        logger.error(f"Can't delete channel for chat ID {event.chat.id}: {e}")
