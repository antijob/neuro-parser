import asyncio
import aiohttp
import time
import logging
import re
from asgiref.sync import sync_to_async

from server.libs.user_agent import session_random_headers
from typing import Coroutine, Iterable
from server.apps.core.models import Article, Source
from server.core.article_parser import ArticleParser
from .statistics import CoroutineStatistics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BadCodeException(Exception):
    def __init__(self, code):
        super().__init__("Bad code")
        self.code = code

async def fetch_url(session: aiohttp.ClientSession, url: str) -> tuple[str, str]:
    params = {}
    if url.startswith("https://t.me/"):
        params = {"embed": "1"}
    try:
        async with session.get(url, params=params) as response:
            if response.ok:
                return [await response.text(), response.url]
            else:
                raise BadCodeException(response.status)
    except aiohttp.ClientError as e:
        logger.error(f"Network error occurred while fetching URL {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error occurred while fetching URL {url}: {e}")
        raise

class Fetcher:
    def __init__(self):
        self.coroutines: list[Coroutine] = []

    @staticmethod
    async def fetch_article(session: aiohttp.ClientSession, article: Article) -> tuple[Article, str]:
        content, resolved_url = await fetch_url(session, article.url)
        if article.url != resolved_url:
            article.redirect_url = resolved_url
            article.is_redirect = True
            await sync_to_async(article.save, thread_sensitive=True)()

            if not Article.objects.filter(url=resolved_url).exists():
                article = Article.objects.create(url=resolved_url, source=article.source)
        article.text = content
        ArticleParser.postprocess_article(article, content)
        await sync_to_async(article.save, thread_sensitive=True)()

        return article, resolved_url

    async def download(self, article: Article) -> Article:
        try:
            async with aiohttp.ClientSession(
                trust_env=True,
                connector=aiohttp.TCPConnector(ssl=False),
                headers=session_random_headers(),
            ) as session:
                article, _ = await self.fetch_article(session, article.url)
                return article
        except Exception as e:
            logger.error(f"Error downloading article {article.url}: {e}")

    @staticmethod
    async def download_source(url: str) -> str:
        if re.match(r"https://t\.me/", url) and "/s/" not in url:
            url = url.replace("https://t.me/", "https://t.me/s/")
        params = {}
        try:
            async with aiohttp.ClientSession(
                trust_env=True,
                connector=aiohttp.TCPConnector(ssl=False),
                headers=session_random_headers(),
            ) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Network error occurred while fetching source URL {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error occurred while fetching source URL {url}: {e}")
            return None

    async def create_coroutine(self, source: Source, articles: dict[str, Article]):
        rps: float = 1
        if ".ok.ru" in source.url or "t.me" in source.url:
            rps = 0.1

        logger.info(f"Start coroutine. Source {source.url}: {len(articles)} articles")
        statistics = CoroutineStatistics(source.url, len(articles))

        async with aiohttp.ClientSession(
            trust_env=True,
            connector=aiohttp.TCPConnector(ssl=False),
            headers=session_random_headers(),
        ) as session:
            delay = 1 / rps

            for url, article in articles.items():
                try:
                    await self.fetch_article(session, article)
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
        results = await asyncio.gather(*self.coroutines)
        return results

    def await_all_coroutines(self) -> int:
        results = asyncio.run(self._await())
        return sum(results)
