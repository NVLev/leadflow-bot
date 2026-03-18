import logging
import httpx

from bot.config import settings

logger = logging.getLogger(__name__)


async def send_lead_to_webhook(lead):
    """
    Отправка лида в Make webhook
    """

    if not settings.webhook.url:
        logger.warning("Webhook URL not set")
        return

    lead_data = {
        "user_id": lead.user_id,
        "name": lead.name,
        "phone": lead.phone,
        "email": lead.email,
        "message": lead.message,
        "created_at": str(lead.created_at),
    }

    logger.info(f"Sending lead to webhook: {lead_data}")

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                settings.webhook.url,
                json=lead_data
            )

        logger.info(f"Webhook status: {response.status_code}")
        logger.info(f"Webhook response: {response.text}")

    except Exception as e:
        logger.exception("Error sending lead to webhook")