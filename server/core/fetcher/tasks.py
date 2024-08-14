import asyncio
import logging

from server.apps.core.models import Article, Source

from .utils import fetcher_session, fetch_article
from .statistics import CoroutineStatistics
from .exceptions import BadCodeException


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def fetch_source_articles(source: Source, articles: list[Article]):
    rps: float = 1
    if ".ok.ru" in source.url or "t.me" in source.url:
        rps = 0.1

    logger.info(f"Start task. Source {source.url}: {len(articles)} articles")
    statistics = CoroutineStatistics(source.url, len(articles))

    async with fetcher_session() as session:
        delay = 1 / rps

        for article in articles:
            try:
                await fetch_article(session, article, source)
                statistics.fetch()
                statistics.postprocess()

                await asyncio.sleep(delay)
            except BadCodeException as e:
                statistics.bad_code(e.code)
            except Exception as e:
                logger.error(f"Task {source.url}: {article.url} exception: {e}")
                statistics.exception()

    logger.info(f"Task finished. Statistics: {statistics}")
    return statistics._postprocess
