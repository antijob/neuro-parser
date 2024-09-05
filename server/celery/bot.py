import asyncio

from aiogram.exceptions import TelegramRetryAfter
from celery.utils.log import get_task_logger

from server.apps.bot.services.inc_post import post_incident
from server.apps.core.models import MediaIncident

from .celery_app import app

logger = get_task_logger(__name__)


class SendMessageTask(app.Task):
    queue = "parser"
    rate_limit = "0.2/s"
    autoretry_for = (TelegramRetryAfter,)
    max_retries = 5
    retry_backoff = 30
    retry_backoff_max = 600
    retry_jitter = False


@app.task(base=SendMessageTask)
def send_incident_notification(media_incident_id: int):
    try:
        media_incident = MediaIncident.objects.get(id=media_incident_id)
    except Exception as e:
        logger.error(f"Could not get media_incident with id {media_incident_id}: {e}")
        return

    try:
        asyncio.run(post_incident(media_incident), debug=True)
        logger.info(f"Notification sent successfully for incident: {media_incident}")
        return
    except Exception as e:
        logger.error(
            f"Error in send_incident_notification for incident {media_incident}: {e}",
            exc_info=True,
        )
        return
