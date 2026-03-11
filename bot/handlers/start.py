from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.menu import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Вы можете оставить заявку, и мы свяжемся с вами.",
        reply_markup=main_menu()
    )