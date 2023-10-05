from .celery_app import app

from server.apps.core.models import Article, Source
from server.apps.core.logic.grabber.fetcher import Fetcher

@app.task(queue="crawler", name='crawl_chain')
def crawl_chain():
    (
        update_sources.s() | 
        fetch_sources.s()
    ).apply_async()


@app.task(queue="crawler")
def update_sources():
    sources = Source.objects.filter(is_active=True)
    for source in sources:
        try:
            source.update()
        except Exception as e:
            print(f"An error occurred while updating source: {e}")


@app.task(queue="crawler")
def fetch_sources(status):
    fetcher = Fetcher()
    sources = Source.objects.filter(is_active=True)
    for source in sources:
        articles = Article.objects.filter(source=source, is_downloaded=False)
        if articles.exists():
            fetcher.add_coroutine(source, articles)
    fetcher.await_all_coroutines()
