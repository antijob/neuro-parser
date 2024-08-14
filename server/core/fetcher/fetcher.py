from typing import Optional
import asyncio
import logging

from typing import Coroutine, Iterable
from server.apps.core.models import Article, Source

from .utils import fetcher_session, fetch_article, fetch_source, prepare_source_url
from .exceptions import BadCodeException, ClientError

from tasks import fetch_source_articles

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
            logger.error(
                f"Network error occurred while fetching source URL {article.url}: {e}"
            )
            return None
        except BadCodeException as e:
            logger.error(f"Fetching bad code for {article.url}: {e.code}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error occurred while fetching article {article.url}: {e}"
            )
            return None

    @staticmethod
    async def download_source(source: Source) -> Optional[str]:
        try:
            async with fetcher_session() as session:
                source_data = await fetch_source(session, source)
                return source_data
        except ClientError as e:
            logger.error(
                f"Network error occurred while fetching source URL {source.url}: {e}"
            )
            return None
        except BadCodeException as e:
            logger.error(f"Fetching bad code for {source.url}: {e.code}")
            return None
        except Exception as e:
            logger.error(
                f"Unexpected error occurred while fetching source URL {source.url}: {e}"
            )
            return None

    def add_task(self, source: Source, articles: Iterable[Article]):
        coro = fetch_source_articles(source, articles)
        self.coroutines.append(coro)

    async def _await(self) -> list[int]:
        results = await asyncio.gather(*self.coroutines, return_exceptions=False)
        return results

    def await_tasks(self) -> int:
        results = asyncio.run(self._await())
        fetched_total = 0
        for res in results:
            if isinstance(res, BaseException):
                logger.error(
                    "Coroutine error occured during one of the tasks: ", exc_info=res
                )
            else:
                fetched_total += res

        return fetched_total
