# fetcher.py
import requests
import asyncio
import aiohttp
import time
from icecream import ic

from server.apps.core.models import Article
from asgiref.sync import sync_to_async
from .user_agent import random_headers


async def fetch_url(session, url):
    params = {}
    if url.startswith('https://t.me/'):
        params = {'embed': '1'}
    async with session.get(url, params=params, headers=random_headers()) as response:
        if response.status == 200:
            return await response.text()
        else:
            print(f"Ошибка при запросе {url}: {response.status}")
            return None


class Fetcher(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Fetcher, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.coroutines = []
    

    async def coroutine(self, source, articles):
        rps = 5 #source.rps
        print("Start coroutine")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            delay = 1 / rps 
            start_time = time.time()
            total_fetch_time = 0
            total_postprocess_time = 0

            for article in articles:
                fetch_start_time = time.time()

                content = await fetch_url(session, article['url'])

                fetch_end_time = time.time()
                total_fetch_time += fetch_end_time - fetch_start_time

                if content is not None:
                    postprocess_start_time = time.time()

                    await sync_to_async(article["article"].get_html_and_postprocess)(content)

                    postprocess_end_time = time.time()
                    total_postprocess_time += postprocess_end_time - postprocess_start_time

                await asyncio.sleep(delay)

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Source {source.url}: {len(articles)} articles by {elapsed_time:.2f}s. Fetch: {total_fetch_time:.2f}s, Parse:{total_postprocess_time:.2f}s")


    def add_coroutine(self, source, articles):
        articles = [{'url': a.url, 'article':a} for a in articles]
        coro = self.coroutine(source, articles)
        self.coroutines.append(coro)

    async def _await(self):
        await asyncio.gather(*self.coroutines)


    def await_all_coroutines(self):
        asyncio.run(self._await())
