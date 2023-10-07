from .celery_app import app
from server.apps.core.logic.grabber import duplicates
from server.apps.core.models import Article, Source
from server.apps.core.logic.reposts import check_repost_query



from datetime import datetime, timedelta


def get_parse_candidates():
    start_date = datetime.now().date() - timedelta(days=3)
    articles = Article.objects.filter(
        is_downloaded=True,
        is_parsed=False,
        publication_date__gte=start_date)
    return articles


@app.task(queue="parser", name='parse_chain')
def parse_chain():
    articles = get_parse_candidates()
    if len(articles) == 0:
        return "No candidates"

    (
        delete_duplicate_articles.s() |
        create_incidents.s() |
        delete_duplicated_incidents.s()
    ).apply_async()
    return f"Start chain with {len(articles)} urls"


@app.task(queue="parser")
def delete_duplicate_articles():
    articles = get_parse_candidates()
    check_repost_query(articles)
    dups = articles.filter(is_duplicate=True)
    return f"Duplicates found: {len(dups)}"


@app.task(queue="parser")
def create_incidents(status):
    articles = get_parse_candidates()
    incidents_count = 0
    for article in articles:
        try:
            res = article.create_incident()
            article.is_parsed = True
            article.save()
            if res:
                incidents_count += 1
        except Exception as e:
            print(f"An error occurred while creating incident for article: {e}")
    return f"Incindens created: {incidents_count}"

@app.task(queue="parser")
def delete_duplicated_incidents(status):
    pass

@app.task(queue="parser")
def rebuild_simhash_index():
    # ToDo
    pass
