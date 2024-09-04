from typing import Coroutine
import asyncio
import logging

from .celery_app import app

from server.apps.core.models import Article, Source
from server.core.fetcher import Fetcher
from server.core.source_parser import SourceParser


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.task(queue="crawler", name="crawl_chain")
def crawl_chain():
    (update_sources.s() | fetch_sources.s()).apply_async()


@app.task(queue="crawler")
def update_sources():
    tasks: list[Coroutine] = []

    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    sources = Source.objects.filter(is_active=True)
    for source in sources:
        tasks.append(SourceParser.create_new_articles(source))

    results = loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=False))

    urls_count = 0
    for res in results:
        if isinstance(res, BaseException):
            logger.error(
                "Coroutine error occured during SourceParser.create_new_articles: ",
                exc_info=res,
            )
        else:
            urls_count += res
    return f"Urls extracted: {urls_count}"


@app.task(queue="crawler")
def fetch_sources(status):
    fetcher = Fetcher()
    sources = Source.objects.filter(is_active=True)
    for source in sources:
        articles = Article.objects.filter(
            source=source, is_downloaded=False, is_redirect=False
        )
        if articles.exists():
            fetcher.add_task(source, articles)
    fetched_count = fetcher.await_tasks()
    return f"Fetcher fetched {fetched_count} urls"
