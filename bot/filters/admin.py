from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from bot.config import settings


class AdminFilter(BaseFilter):
    """Пропускает только пользователей из списка admin_ids."""

    async def __call__(self, event: Message | CallbackQuery) -> bool:
        user_id = event.from_user.id if event.from_user else None
        return user_id in settings.bot.admin_ids
