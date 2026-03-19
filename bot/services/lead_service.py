import logging
from typing import Any, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.database.models import Lead
from bot.database.schemas import LeadCreate
from bot.services.webhook_service import send_lead_to_webhook

logger = logging.getLogger(__name__)


async def create_lead(
    session: AsyncSession,
    data: LeadCreate,
) -> Lead:
    logger.info("Creating lead for user %s", data.user_id)

    lead = Lead(
        user_id=data.user_id,
        name=data.name,
        phone=data.phone,
        email=data.email,
        message=data.message,
    )

    session.add(lead)

    await session.commit()
    await session.refresh(lead)
    try:
        await send_lead_to_webhook(lead)
    except Exception:
        logger.exception("Webhook failed but lead is saved")

    return lead


async def get_leads_page(
    session: AsyncSession,
    page: int = 0,
) -> tuple[Sequence[Any], int]:
    """Возвращает страницу заявок и общее количество страниц."""
    page_size = settings.pagination.leads_page_size

    count_result = await session.execute(select(func.count()).select_from(Lead))
    total = count_result.scalar_one()
    total_pages = max(1, (total + page_size - 1) // page_size)

    stmt = (
        select(Lead)
        .order_by(Lead.created_at.desc())
        .offset(page * page_size)
        .limit(page_size)
    )
    result = await session.execute(stmt)
    leads = result.scalars().all()

    return leads, total_pages


async def update_lead_status(
    session: AsyncSession,
    lead_id: int,
    status: str,
):

    stmt = select(Lead).where(Lead.id == lead_id)

    result = await session.execute(stmt)

    lead = result.scalar_one_or_none()

    if not lead:
        return None

    lead.status = status

    await session.commit()

    return lead
