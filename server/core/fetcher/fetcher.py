from typing import Optional
import asyncio
import logging

from typing import Coroutine, Iterable
from server.apps.core.models import Article, Source

from .utils import fetcher_session, fetch_article, prepare_source_url
from .statistics import CoroutineStatistics
from .exceptions import BadCodeException, ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Fetcher:
    def __init__(self):
        self.coroutines: list[Coroutine] = []

    @staticmethod
    async def download_article(article: Article, source: Source) -> Optional[Article]:
        try:
            async with fetcher_session() as session:
                article, _ = await fetch_article(session, article.url, source)
                return article
        except ClientError as e:
            logger.error(f"Network error occurred while fetching source URL {url}: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error occurred while fetching article {article.url}: {e}"
            )
            return None

    @staticmethod
    async def download_source(url: str) -> Optional[str]:
        url = prepare_source_url(url)

        try:
            async with fetcher_session() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None

                    return await response.text()
        except ClientError as e:
            logger.error(f"Network error occurred while fetching source URL {url}: {e}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error occurred while fetching source URL {url}: {e}"
            )
            return None

    async def create_coroutine(self, source: Source, articles: dict[str, Article]):
        rps: float = 1
        if ".ok.ru" in source.url or "t.me" in source.url:
            rps = 0.1

        logger.info(f"Start coroutine. Source {source.url}: {len(articles)} articles")
        statistics = CoroutineStatistics(source.url, len(articles))

        async with fetcher_session() as session:
            delay = 1 / rps

            for url, article in articles.items():
                try:
                    await fetch_article(session, article, source)
                    statistics.fetch()
                    statistics.postprocess()

                    await asyncio.sleep(delay)
                except BadCodeException as e:
                    statistics.bad_code(e.code)
                except Exception as e:
                    logger.error(f"Coroutine {source.url}: {url} exception: {e}")
                    statistics.exception()

        logger.info(f"Coroutine finished. Statistics: {statistics}")
        return statistics._postprocess

    def add_coroutine(self, source: Source, articles: Iterable[Article]):
        articles_dict: dict[str, Article] = {a.url: a for a in articles}
        coro = self.create_coroutine(source, articles_dict)
        self.coroutines.append(coro)

    async def _await(self) -> list[int]:
        results = await asyncio.gather(*self.coroutines, return_exceptions=False)
        return results

    def await_all_coroutines(self) -> int:
        results = asyncio.run(self._await())
        fetched_total = 0
        for res in results:
            if isinstance(res, BaseException):
                logger.error("Coroutine exception: ", exc_info=res)
            else:
                fetched_total += res

        return fetched_total
