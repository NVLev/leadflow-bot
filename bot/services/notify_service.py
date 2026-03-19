import logging

from aiogram import Bot

from bot.config import settings
from bot.database.enums import LeadStatus
from bot.database.models import Lead
from bot.keyboards.admin_kb import STATUS_LABELS, lead_status_keyboard

logger = logging.getLogger(__name__)


def format_lead_for_admin(lead: Lead) -> str:
    status_label = STATUS_LABELS.get(LeadStatus(lead.status), lead.status)
    email_line = f"📧 Email: {lead.email}" if lead.email else "📧 Email: —"
    service_line = f"🔧 Услуга: {lead.service}" if lead.service else ""

    lines = [
        f"📥 <b>Новая заявка #{lead.id}</b>\n",
        f"👤 Имя: {lead.name}",
        f"📞 Телефон: {lead.phone}",
        email_line,
    ]
    if service_line:
        lines.append(service_line)

    lines += [
        f"💬 Сообщение: {lead.message or '—'}",
        f"\n📊 Статус: {status_label}",
        f"🕐 Время: {lead.created_at.strftime('%d.%m.%Y %H:%M')}",
    ]

    return "\n".join(lines)


async def notify_admins(bot: Bot, lead: Lead) -> None:
    text = format_lead_for_admin(lead)
    keyboard = lead_status_keyboard(lead.id, lead.status)

    for admin_id in settings.bot.admin_ids:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML",
            )
            logger.info("Lead notification sent to admin %s", admin_id)
        except Exception:
            logger.exception("Failed to notify admin %s", admin_id)
