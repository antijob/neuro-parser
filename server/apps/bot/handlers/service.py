from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from server.apps.bot.data.messages import HELP_MESSAGE

router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    await message.answer(text=HELP_MESSAGE)


@router.message(Command("help"))
async def help_command(message: Message):
    await message.answer(text=HELP_MESSAGE)
