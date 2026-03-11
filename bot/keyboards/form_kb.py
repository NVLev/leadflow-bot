from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def cancel_keyboard():

    keyboard = [
        [KeyboardButton(text="❌ Отмена")]
    ]

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )