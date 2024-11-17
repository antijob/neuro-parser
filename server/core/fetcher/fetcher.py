from typing import Optional
import asyncio
import logging

from typing import Coroutine, Iterable
from server.apps.core.models import Article, Source


from .libs.exceptions import BadCodeException, ClientError
from .tasks import fetch_source_articles
from .clients import ClientFactory, ClientSourceData

# Configure logging
logger = logging.getLogger(__name__)


class Fetcher:
    def __init__(self):
        self.coroutines: list[Coroutine] = []

    @staticmethod
    async def download_article(
        article: Article, source: Optional[Source] = None
    ) -> Optional[Article]:
        try:
            async with ClientFactory.get_client(source, article) as client:
                return await client.get_article(article, source)
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
    async def download_source(source: Source) -> ClientSourceData:
        try:
            async with ClientFactory.get_client(source) as client:
                return await client.get_source(source)
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
        coro = fetch_source_articles(source, list(articles))
        self.coroutines.append(coro)

    def await_tasks(self) -> int:
        async def gather(tasks):
            return await asyncio.gather(*tasks, return_exceptions=True)

        results = asyncio.run(gather(self.coroutines))

        fetched_total = 0
        for res in results:
            if isinstance(res, BaseException):
                logger.error(
                    "Coroutine error occured during one of the tasks: ", exc_info=res
                )
            else:
                fetched_total += res

        return fetched_total
