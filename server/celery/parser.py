from .celery_app import app
from server.apps.core.logic.grabber import duplicates
from server.apps.core.models import Article, Source


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
    # ToDo: get only unparsed articles for last 3 days
    articles = Article.objects.filter(is_downloaded=True, is_incident_created=False)
    for article in articles:
        try:
            article.create_incident()
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