from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_menu():

    keyboard = [
        [KeyboardButton(text="📩 Оставить заявку")],
        [KeyboardButton(text="ℹ️ О сервисе")],
    ]

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
