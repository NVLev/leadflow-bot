from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.menu import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "👋 Добро пожаловать!\n\n" "Вы можете оставить заявку, и мы свяжемся с вами.",
        reply_markup=main_menu(),
    )


@router.message(F.text == "ℹ️ О сервисе")
async def info(message: Message):
    await message.answer(
        "📋 <b>Как это работает</b>\n\n"
        "Вы оставляете заявку прямо здесь, в Telegram — "
        "без звонков и форм на сайте.\n\n"
        "Мы получаем её мгновенно и свяжемся с вами "
        "удобным способом в течение рабочего дня.\n\n"
        "📞 Если хотите поговорить прямо сейчас — "
        "напишите нам: @your_contact",
        parse_mode="HTML",
    )
