from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Lead
from bot.database.schemas import LeadCreate
from bot.services.webhook_service import send_lead_to_webhook

import logging

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

async def get_leads(
    session: AsyncSession,
):

    stmt = select(Lead).order_by(Lead.created_at.desc())

    result = await session.execute(stmt)

    return result.scalars().all()

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