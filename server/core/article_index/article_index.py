import redis.asyncio as redis
import logging
from simhash import Simhash, SimhashIndex
import re
from server.apps.core.models import Article
from datetime import datetime, timedelta
from typing import List


SIMHASH_INDEX_KEY = "simhash-index"
SIMHASH_INDEX_TIMEOUT = 3600 * 3  # 3 hours
SIMHASH_DIMENSION = 256
SIMHASH_TOLERANCE = 8
clear_text = re.compile(r"http\S+")  # remove links


def get_latest_unique_articles() -> List[Article]:
    start_date = datetime.now().date() - timedelta(days=3)
    articles = Article.objects.filter(
        is_downloaded=True,
        # is_parsed=False,
        is_duplicate=False,
        create_date__gte=start_date,
    )
    return articles


def make_simhash_from_article_text(text: str) -> Simhash:
    text = text.strip()
    text = text.lower()
    text = clear_text.sub("", text)
    return Simhash(text, f=SIMHASH_DIMENSION)


def get_simhash_distance(url1, url2):
    text1 = Article.objects.get(url=url1).text
    text2 = Article.objects.get(url=url2).text
    sh1 = make_simhash_from_article_text(text1)
    sh2 = make_simhash_from_article_text(text2)
    return sh1.distance(sh2)


class SingletonMeta(type):
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kwargs)

        return cls.instance


class ArticleIndex(metaclass=SingletonMeta):
    redis_client = redis.StrictRedis(host="redis", port=6379, db=0)
    simhashIndex: SimhashIndex

    async def load(self) -> None:
        self.simhashIndex = self.redis_client.get(SIMHASH_INDEX_KEY)
        if self.simhashIndex is None:
            index_articles = get_latest_unique_articles()
            self.create_index(index_articles)

    async def save(self) -> None:
        self.redis_client.set(
            SIMHASH_INDEX_KEY, self.simhashIndex, ex=SIMHASH_INDEX_TIMEOUT
        )

    def create_index(self, articles: List[Article]) -> None:
        objs = [(art.url, make_simhash_from_article_text(art.text)) for art in articles]

        # logging.basicConfig()
        sh_log = logging.getLogger().setLevel(logging.ERROR)  # silent index
        self.simhashIndex = SimhashIndex(
            objs, f=SIMHASH_DIMENSION, k=SIMHASH_TOLERANCE, log=sh_log
        )

    def get_neighbours(self, article: Article) -> List[str]:
        if not article.text:
            return []
        sh = make_simhash_from_article_text(article.text)
        return self.simhashIndex.get_near_dups(sh)

    def add(self, article: Article) -> None:
        if not article.text:
            return
        sh = make_simhash_from_article_text(article.text)
        self.simhashIndex.add(article.url, sh)
