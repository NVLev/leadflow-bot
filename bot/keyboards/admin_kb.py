from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.enums import LeadStatus


STATUS_LABELS = {
    LeadStatus.NEW: "🆕 Новая",
    LeadStatus.PROCESSED: "✅ Обработана",
    LeadStatus.SENT_TO_CRM: "📤 Отправлена в CRM",
    LeadStatus.REJECTED: "❌ Отклонена",
}

STATUS_USER_MESSAGES = {
    LeadStatus.PROCESSED: "✅ Ваша заявка обработана. Менеджер свяжется с вами в ближайшее время.",
    LeadStatus.SENT_TO_CRM: "📋 Ваша заявка передана в работу.",
    LeadStatus.REJECTED: "❌ К сожалению, по вашей заявке принято отрицательное решение. Если есть вопросы — обратитесь снова.",
}


def lead_status_keyboard(lead_id: int, current_status: str) -> InlineKeyboardMarkup:
    """Клавиатура смены статуса под уведомлением об админа."""
    builder = InlineKeyboardBuilder()

    for status in LeadStatus:
        if status.value == current_status:
            continue
        builder.button(
            text=STATUS_LABELS[status],
            callback_data=f"set_status:{lead_id}:{status.value}",
        )

    builder.adjust(2)
    return builder.as_markup()


def leads_pagination_keyboard(page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Клавиатура пагинации для /leads."""
    builder = InlineKeyboardBuilder()

    if page > 0:
        builder.button(text="◀️ Назад", callback_data=f"leads_page:{page - 1}")
    if page < total_pages - 1:
        builder.button(text="Вперёд ▶️", callback_data=f"leads_page:{page + 1}")

    builder.adjust(2)
    return builder.as_markup()