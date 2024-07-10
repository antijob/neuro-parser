import asyncio
import aiohttp
import time
from asgiref.sync import sync_to_async
import re

from server.libs.user_agent import session_random_headers

from typing import Coroutine, Iterable, List, Dict

from server.apps.core.models import Article, Source
from server.core.article_parser import ArticleParser

from .statistics import CoroutineStatistics


class BadCodeException(Exception):
    def __init__(self, code):
        super().__init__("Bad code")

        self.code = code


async def fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    params = {}
    if url.startswith("https://t.me/"):
        params = {"embed": "1"}
    async with session.get(url, params=params) as response:  # aiohttp.ClientResponse
        if response.status == 200:
            return await response.text()
        else:
            raise BadCodeException(response.status)


# Должен ли это быть синглетон? Чтобы он мог держать рпс, сколько бы раз его не запустили? Или дизайн его создан не для этого? Или для этих целей надо создавать некоторую обертку над ним?
class Fetcher:
    def __init__(self):
        self.coroutines: List[Coroutine] = []

    async def download(self, article: Article) -> None:
        async with aiohttp.ClientSession(
            trust_env=True,
            connector=aiohttp.TCPConnector(ssl=False),
            headers=session_random_headers(),
        ) as session:
            content = await fetch_url(session, article.url)
            article.text = content
            ArticleParser.postprocess_article(article, content)
            await sync_to_async(article.save, thread_sensitive=True)()

    async def download_source(url: str) -> str:
        if re.match(r"https://t\.me/", url) and "/s/" not in url:
            url = url.replace("https://t.me/", "https://t.me/s/")
        params = {}
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

    async def create_coroutine(self, source: Source, articles: Dict[str, Article]):
        rps: float = 1  # source.rps
        if ".ok.ru" in source.url or "t.me" in source.url:
            rps = 0.1

        print(f"Start coroutine. Source {source.url}: {len(articles)} articles")
        statistics = CoroutineStatistics(source.url, len(articles))

        async with aiohttp.ClientSession(
            trust_env=True,
            connector=aiohttp.TCPConnector(ssl=False),
            headers=session_random_headers(),
        ) as session:
            delay = 1 / rps
            statistics.start()

            for url, article in articles.items():
                try:
                    statistics.fetch_start()
                    content = await fetch_url(session, url)
                    statistics.fetched()

                    postprocess_start_time = time.time()
                    ArticleParser.postprocess_article(article, content)
                    await sync_to_async(article.save, thread_sensitive=True)()
                    postprocess_end_time = time.time()
                    statistics.postprocess(
                        postprocess_end_time - postprocess_start_time
                    )

                    await asyncio.sleep(delay)
                except BadCodeException as e:
                    statistics.bad_code(e.code)
                except Exception as e:
                    print(f"Coroutine {source.url}: {url} exception: {e}")
                    statistics.exception()

            statistics.finish()
            print(statistics)

    def add_coroutine(self, source: Source, articles: Iterable[Article]):
        articles_dict: Dict[str, Article]
        articles_dict = {a.url: a for a in articles}
        coro = self.create_coroutine(source, articles_dict)

        self.coroutines.append(coro)

    async def _await(self):
        await asyncio.gather(*self.coroutines)

    def await_all_coroutines(self):
        asyncio.run(self._await())
