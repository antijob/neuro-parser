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
    async with session.get(url, headers=random_headers()) as response:
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
        print("Запускаем корутинку")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            delay = 1 / rps 
            start_time = time.time()

            for article in articles:
                content = await fetch_url(session, article['url'])
                if content is not None:
                    await sync_to_async(article["article"].get_html_and_postprocess)(content)

                await asyncio.sleep(delay)

            end_time = time.time()
            elapsed_time = end_time - start_time
            ic(f"Из источника {source.url} было прокачано {len(articles)} статей за {elapsed_time:.2f} секунд")

    def add_coroutine(self, source, articles):
        articles = [{'url': a.url, 'article':a} for a in articles]
        coro = self.coroutine(source, articles)
        self.coroutines.append(coro)

    async def _await(self):
        await asyncio.gather(*self.coroutines)


    def await_all_coroutines(self):
        asyncio.run(self._await())
