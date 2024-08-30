import asyncio
from datetime import datetime, timedelta
from itertools import islice

from aiogram.exceptions import TelegramRetryAfter
from celery import group
from celery.utils.log import get_task_logger

from server.apps.bot.services.inc_post import post_incident
from server.apps.core.models import Article, MediaIncident
from server.core.article_index.query_checker import mark_duplicates
from server.core.incident_predictor import IncidentPredictor
from server.settings.components.celery import INCIDENT_BATCH_SIZE

from .celery_app import app

logger = get_task_logger(__name__)


def split_every(n, iterable):
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield piece
        piece = list(islice(i, n))


def get_parse_candidates():
    start_date = datetime.now().date() - timedelta(days=3)
    articles = Article.objects.filter(
        is_downloaded=True,
        is_parsed=False,
        is_duplicate=False,
        create_date__gte=start_date,
    )
    return articles


@app.task(queue="parser", name="parse_chain")
def parse_chain():
    articles = get_parse_candidates()

    if len(articles) == 0:
        return "No candidates"
    (mark_duplicate_articles.s() | plan_incidents.s()).apply_async()

    return f"Start chain with {len(articles)} urlsss"


@app.task(queue="parser")
def mark_duplicate_articles():
    articles = get_parse_candidates()
    mark_duplicates(articles)
    dups = articles.filter(is_duplicate=True)
    return f"Duplicates found: {len(dups)}"


@app.task(queue="parser")
def plan_incidents(status):
    articles = get_parse_candidates()
    tasks = []
    for batch in split_every(int(INCIDENT_BATCH_SIZE), articles):
        tasks.append(create_incidents.s([art.url for art in batch]))
    task_group = group(tasks)
    task_group.apply_async()
    return "Group of create_incidents tasks submitted"


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
    logger.info(f"Starting send_incident_notification for id: {media_incident_id}")
    try:
        media_incident = MediaIncident.objects.get(id=media_incident_id)
    except Exception as e:
        logger.error(f"Could not get media_incident with id {media_incident_id}: {e}")
        return f"MediaIncident getting failed due to an error: {e}"

    logger.info(f"Retrieved MediaIncident: {media_incident}")

    try:
        logger.info(f"Attempting to send notification for incident: {media_incident}")
        asyncio.run(post_incident(media_incident), debug=True)
        logger.info(f"Notification sent successfully for incident: {media_incident}")
        return f"Notification sent for incident: {media_incident}"
    except Exception as e:
        logger.error(
            f"Error in send_incident_notification for incident {media_incident}: {e}",
            exc_info=True,
        )
        return f"Notification failed due to an error: {e}"


@app.task(queue="parser")
def create_incidents(batch):
    logger.info(f"Starting create_incidents for batch size: {len(batch)}")
    try:
        articles_batch = []
        for url in batch:
            try:
                article = Article.objects.get(url=url)
                articles_batch.append(article)
                logger.info(f"Retrieved article: {article}")
            except Exception as e:
                logger.error(f"Error retrieving article with url {url}: {e}")

        logger.info(
            f"Retrieved {len(articles_batch)} articles out of {len(batch)} urls"
        )

        predictor = IncidentPredictor()
        incidents_created = predictor.predict_batch(articles_batch)
        incidents_count = len(incidents_created)

        logger.info(f"Predicted {incidents_count} incidents")

        for art in articles_batch:
            art.is_parsed = True
            art.save()
            logger.info(f"Marked article as parsed: {art}")

        for incident in incidents_created:
            logger.info(f"Queueing notification for incident: {incident}")
            send_incident_notification.delay(incident.id)

        logger.info(f"Batch finished. Incidents created: {incidents_count}")
        return f"Batch finished. Incidents created: {incidents_count}"
    except Exception as e:
        logger.error(f"Error in create_incidents: {e}", exc_info=True)
        return f"Batch failed due to an error: {e}"


@app.task(queue="parser")
def rebuild_simhash_index():
    # ToDo: Раз в день, не реже, перестраивать индекс с нуля
    pass
