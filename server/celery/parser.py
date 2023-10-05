from .celery_app import app
from server.apps.core.logic.grabber import duplicates
from server.apps.core.models import Article, Source

from datetime import datetime, timedelta


@app.task(queue="parser", name='parse_chain')
def parse_chain():
    (
        delete_duplicate_articles.s() | 
        create_incidents.s() |
        delete_duplicated_incidents.s()
    ).apply_async()


@app.task(queue="parser")
def delete_duplicate_articles():
    # simhash index will be here
    return True


@app.task(queue="parser")
def create_incidents(status):
    start_date = datetime.now().date() - timedelta(days=3)
    articles = Article.objects.filter(
        is_downloaded=True, 
        is_parsed=False,
        publication_date__gte=start_date)

    for article in articles:
        try:
            article.create_incident()
            article.is_parsed = True
            article.save()
        except Exception as e:
            print(f"An error occurred while creating incident for article: {e}")


@app.task(queue="parser")
def delete_duplicated_incidents(status):
    pass


@app.task(queue="parser")
def search_duplicates(article_id):
    article = Article.objects.get(pk=article_id)
    history = Article.objects.filter(incident__isnull=False)
    duplicates.search_duplicates_in_history([article], history)


@app.task(queue="parser")
def rebuild_simhash_index():
    # ToDo
    pass