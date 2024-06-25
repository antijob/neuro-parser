import asyncio
import aiohttp
import time
from asgiref.sync import sync_to_async

from server.libs.user_agent import session_random_headers

from typing import Callable, Awaitable, Any, Coroutine, Iterable, List, Dict

from server.apps.core.models import Article, Source
from server.core.parser.article_parser import ArticleParser


class BadCodeException(Exception):
    def __init__(self, code):
        super().__init__("Bad code")

        self.code = code


class CoroutineStatistics:
    def __init__(self, source: str, article_numbers: int):
        self.source: str = source
        self.len: int = article_numbers
        self.fetches: int = 0
        self.success: int = 0
        self.bad_codes: int = 0
        self.exceptions: int = 0
        self.codes: Dict[int, int] = {}

        self.start_time: float = 0
        self.elapsed_time: float = 0
        self.fetch_time: float = 0
        self.postprocess_time: float = 0
        self.fetch_start_time: float = 0

    def start(self):
        self.start_time = time.time()

    def finish(self):
        end_time = time.time()
        self.elapsed_time = end_time - self.start_time

    def exception(self):
        self.exceptions += 1

    def postprocess(self, time: float):
        self.postprocess_time += time
        self.success += 1

    def fetch_start(self):
        self.fetch_start_time = time.time()

    def fetched(self):
        fetch_end_time = time.time()
        self.fetch_time += fetch_end_time - self.fetch_start_time
        self.fetches += 1

    def bad_code(self, code: int):
        self.bad_codes += 1
        if code in self.codes:
            self.codes[code] += 1
        else:
            self.codes[code] = 1

    def __str__(self):
        codes_str = ""
        if len(self.codes) > 0:
            codes_str = "\nBad codes info: "
            for code, count in self.codes.items():
                codes_str += f'"{code}": {count}, '
        return (
            f"Coroutine finished. Source: {self.source}: {self.len} articles by {self.elapsed_time:.2f}s.\n"
            f"Fetch time: {self.fetch_time:.2f}s, Parse time:{self.postprocess_time:.2f}s\n"
            f"Succeded: {self.success}, Fetched: {self.fetches}, Bad Codes: {self.bad_codes}, Exceptions: {self.exceptions}"
            f"{codes_str}"
        )


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
