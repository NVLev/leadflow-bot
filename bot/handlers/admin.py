# bot/handlers/admin.py

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from bot.database.db_helper import db_helper
from bot.database.enums import LeadStatus
from bot.database.models import Lead
from bot.keyboards.admin_kb import (
    STATUS_LABELS,
    STATUS_USER_MESSAGES,
    lead_status_keyboard,
    leads_pagination_keyboard,
)
from bot.services.lead_service import get_leads_page, update_lead_status
from bot.services.notify_service import format_lead_for_admin
from bot.filters.admin import AdminFilter

import logging

logger = logging.getLogger(__name__)

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())


def format_leads_page(leads, page: int, total_pages: int) -> str:
    if not leads:
        return "📭 Заявок пока нет."

    lines = [f"📋 <b>Заявки</b> (стр. {page + 1}/{total_pages})\n"]
    for lead in leads:
        status_label = STATUS_LABELS.get(LeadStatus(lead.status), lead.status)
        email = lead.email or "—"
        lines.append(
            f"<b>#{lead.id}</b> {lead.name} | {lead.phone} | {email}\n"
            f"   💬 {lead.message[:50]}{'...' if len(lead.message) > 50 else ''}\n"
            f"   {status_label} · {lead.created_at.strftime('%d.%m %H:%M')}\n"
        )
    return "\n".join(lines)


async def _get_leads_page(page: int) -> tuple[list[Lead], int] | None:
    """Обёртка для вызова get_leads_page через session_getter."""
    async for session in db_helper.session_getter():
        return await get_leads_page(session, page=page)


async def _update_status(lead_id: int, status: str):
    """Обёртка для вызова update_lead_status через session_getter."""
    async for session in db_helper.session_getter():
        return await update_lead_status(session, lead_id, status)


@router.message(Command("leads"))
async def cmd_leads(message: Message) -> None:
    leads, total_pages = await _get_leads_page(page=0)

    text = format_leads_page(leads, page=0, total_pages=total_pages)
    keyboard = leads_pagination_keyboard(page=0, total_pages=total_pages)

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("leads_page:"))
async def paginate_leads(callback: CallbackQuery) -> None:
    page = int(callback.data.split(":")[1])

    leads, total_pages = await _get_leads_page(page=page)

    text = format_leads_page(leads, page=page, total_pages=total_pages)
    keyboard = leads_pagination_keyboard(page=page, total_pages=total_pages)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(F.data.startswith("set_status:"))
async def set_lead_status(callback: CallbackQuery, bot: Bot) -> None:
    _, lead_id_str, new_status = callback.data.split(":")
    lead_id = int(lead_id_str)

    lead = await _update_status(lead_id, new_status)

    if not lead:
        await callback.answer("⚠️ Заявка не найдена", show_alert=True)
        return

    updated_text = format_lead_for_admin(lead)
    updated_keyboard = lead_status_keyboard(lead.id, lead.status)
    await callback.message.edit_text(
        updated_text, reply_markup=updated_keyboard, parse_mode="HTML"
    )

    status_label = STATUS_LABELS.get(LeadStatus(new_status), new_status)
    await callback.answer(f"Статус изменён: {status_label}")

    user_message = STATUS_USER_MESSAGES.get(LeadStatus(new_status))
    if user_message and lead.user_id:
        try:
            await bot.send_message(chat_id=lead.user_id, text=user_message)
        except Exception:
            logger.exception(
                "Failed to notify user %s about status change", lead.user_id
            )