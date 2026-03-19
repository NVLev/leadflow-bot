from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

SERVICES = [
    "💬 Консультация",
    "📐 Замер / выезд",
    "🛠 Ремонт / монтаж",
    "📦 Другое",
]


def service_keyboard() -> InlineKeyboardMarkup:
    """Inline-клавиатура выбора услуги."""
    builder = InlineKeyboardBuilder()
    for service in SERVICES:
        builder.button(text=service, callback_data=f"service:{service}")
    builder.adjust(2)
    return builder.as_markup()


def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )