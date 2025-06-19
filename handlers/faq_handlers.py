from aiogram import Router, F
from aiogram.types import Message
from texts import FAQ_TEXT, BUTTON_FAQ
from keyboards import main_menu

router = Router()

@router.message(F.text == BUTTON_FAQ)
async def faq_handler(message: Message):
    await message.answer(FAQ_TEXT, parse_mode="HTML", reply_markup=main_menu())
