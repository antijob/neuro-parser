from .celery_app import app
from server.apps.core.models import Article, Source
from server.apps.core.incident_types import IncidentType
from server.core.article_index.query_checker import check_repost_query
from server.settings.components.celery import INCIDENT_BATCH_SIZE

from datetime import datetime, timedelta
from itertools import islice
from celery import group


def split_every(n, iterable):
    i = iter(iterable)
    piece = list(islice(i, n))
    while piece:
        yield piece
        piece = list(islice(i, n))


def get_parse_candidates():
    start_date = datetime.now().date() - timedelta(days=3)
    articles = Article.objects.filter(
        is_downloaded=True, is_parsed=False, create_date__gte=start_date
    )
    return articles


@app.task(queue="parser", name="parse_chain")
def parse_chain():
    articles = get_parse_candidates()

    if len(articles) == 0:
        return "No candidates"
    (delete_duplicate_articles.s() | plan_incidents.s()).apply_async()

    return f"Start chain with {len(articles)} urlsss"


@app.task(queue="parser")
def delete_duplicate_articles():
    articles = get_parse_candidates()
    check_repost_query(articles)
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
    return f"Group of create_incidents tasks submitted"


@app.task(queue="parser")
def create_incidents(batch):
    articles_batch = [Article.objects.get(url=url) for url in batch]
    incidents_count = 0
    for incident_type in IncidentType.objects.all():  # filter(is_active=True):
        try:
            incidents_count += incident_type.process_batch(articles_batch)
        except Exception as e:
            print(
                f"An error occurred while creating incident for type {incident_type.description}: {e}"
            )
    for art in articles_batch:
        art.is_parsed = True
        art.save()
    return f"Batch finished. Incodents created: {incidents_count}"


@app.task(queue="parser")
def rebuild_simhash_index():
    # ToDo
    pass
