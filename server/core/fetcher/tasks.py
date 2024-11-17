import asyncio
import logging

from server.apps.core.models import Article, Source

from .clients import ClientFactory
from .libs.statistics import CoroutineStatistics
from .libs.exceptions import BadCodeException


# Configure logging
logger = logging.getLogger(__name__)


async def fetch_source_articles(source: Source, articles: list[Article]):
    rps: float = 1
    if ".ok.ru" in source.url or "t.me" in source.url:
        rps = 0.1

    articles_length = len(articles)
    logger.info(f"Start task. Source {source.url}: {articles_length} articles")
    statistics = CoroutineStatistics(source.url, articles_length)

    async with ClientFactory.get_client(source) as client:
        delay = 1 / rps

        for article in articles:
            try:
                await client.get_article(article, source)

                statistics.fetch()
                await asyncio.sleep(delay)
            except BadCodeException as e:
                statistics.bad_code(e.code)
            except Exception as e:
                logger.error(f"Task {source.url}: {article.url} exception: {e}")
                statistics.exception()

    logger.info(f"Task finished. Statistics: {statistics}")
    return statistics._fetch
