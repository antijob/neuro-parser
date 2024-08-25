import asyncio
import logging
from datetime import datetime, timedelta
from itertools import islice

from celery import group

from server.apps.bot.services.inc_post import mediaincident_post
from server.apps.core.models import Article, MediaIncident
from server.core.article_index.query_checker import mark_duplicates
from server.core.incident_predictor import IncidentPredictor
from server.settings.components.celery import INCIDENT_BATCH_SIZE

from .celery_app import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


@app.task(queue="parser")
def send_incident_notification(media_incident: MediaIncident):
    try:
        asyncio.run(mediaincident_post(media_incident))
        return f"Notification sent for incident: {media_incident}"
    except Exception as e:
        logger.error(f"Error in send_incident_notification: {e}")
        return f"Notification failed due to an error: {e}"


@app.task(queue="parser")
def create_incidents(batch):
    try:
        articles_batch = [Article.objects.get(url=url) for url in batch]

        predictor = IncidentPredictor()
        incidents_created = predictor.predict_batch(articles_batch)
        incidents_count = len(incidents_created)

        for art in articles_batch:
            art.is_parsed = True
            art.save()

        for incindent in incidents_created:
            send_incident_notification.delay(incindent)

        return f"Batch finished. Incidents created: {incidents_count}"
    except Exception as e:
        logger.error(f"Error in create_incidents: {e}")
        return f"Batch failed due to an error: {e}"


@app.task(queue="parser")
def rebuild_simhash_index():
    # ToDo: Раз в день, не реже, перестраивать индекс с нуля
    pass
