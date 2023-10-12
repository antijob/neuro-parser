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
    urls_count = 0
    for source in sources:
        try:
            urls_count += source.update()
        except Exception as e:
            print(f"An error occurred while updating source: {e}")
    return f"Urls extracted: {urls_count}"


@app.task(queue="crawler")
def fetch_sources():
    fetcher = Fetcher()
    sources = Source.objects.filter(is_active=True)
    for source in sources:
        articles = Article.objects.filter(is_downloaded=False)
        if articles.exists():
            fetcher.add_coroutine(source, articles)
    fetcher.await_all_coroutines()
    return "Fetcher fetched some amount of urls"
