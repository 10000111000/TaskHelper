from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from keyboards import main_menu
from texts import START_TEXT, HELP_TEXT

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(START_TEXT, reply_markup=main_menu())

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(HELP_TEXT, reply_markup=main_menu())
