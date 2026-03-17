import logging
from aiogram import Bot

from bot.config import settings
from bot.database.models import Lead

logger = logging.getLogger(__name__)


async def notify_admins(bot: Bot, lead: Lead):

    if not settings.bot.admin_ids:
        logger.warning("No admin IDs configured")
        return

    text = (
        "📩 Новая заявка\n\n"
        f"ID: {lead.id}\n"
        f"Имя: {lead.name}\n"
        f"Телефон: {lead.phone}\n"
        f"Email: {lead.email or '-'}\n"
        f"Комментарий: {lead.message}"
        f"👤 tg://user?id={lead.user_id}"
    )

    for admin_id in settings.bot.admin_ids:

        try:
            await bot.send_message(admin_id, text)
            logger.info("Lead notification sent to admin %s", admin_id)

        except Exception:
            logger.exception("Failed to send notification to admin %s", admin_id)