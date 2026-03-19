import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.config import settings

from bot.handlers import start, form, common, admin
from bot.utils.logger import setup_logger

logger = setup_logger()

async def main():

    bot = Bot(token=settings.bot.token)

    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(start.router)
    dp.include_router(form.router)
    dp.include_router(admin.router)


    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())