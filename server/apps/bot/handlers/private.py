from aiogram import F, Router
from aiogram.types import Message

from server.apps.bot.data.messages import PM_MESSAGE

router = Router()


@router.message(F.chat.type == "private")
async def pm_message(message: Message):
    await message.answer(PM_MESSAGE)
