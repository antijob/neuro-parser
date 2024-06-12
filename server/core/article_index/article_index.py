from django.core.cache import cache

import logging
from simhash import Simhash, SimhashIndex
import re
from server.apps.core.models import Article
from datetime import datetime, timedelta
from typing import List

# from server.lib.singleton import SingletonMeta


SIMHASH_INDEX_KEY_TEMPLATE = "simhash-index-{dim}-{tol}"
SIMHASH_DIMENSION = 128
SIMHASH_TOLERANCE = 8
SIMHASH_INDEX_TIMEOUT = 3600 * 3  # 3 hours
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


class ArticleIndex:
    simhashIndex: SimhashIndex

    def __init__(
        self,
        dimension: int = SIMHASH_DIMENSION,
        tolerance: int = SIMHASH_TOLERANCE,
    ):
        self.simhashIndex = None
        self.dimension = dimension
        self.tolerance = tolerance
        self.key = SIMHASH_INDEX_KEY_TEMPLATE.format(dim=dimension, tol=tolerance)

    def load(self) -> None:
        cachedIndex = cache.get(self.key)
        if cachedIndex is None:
            index_articles = get_latest_unique_articles()
            self.create_index(index_articles)
        else:
            self.simhashIndex = cachedIndex

    def save(self) -> None:
        cache.set(self.key, self.simhashIndex, SIMHASH_INDEX_TIMEOUT)

    def create_index(self, articles: List[Article]) -> None:
        objs = [(art.url, make_simhash_from_article_text(art.text)) for art in articles]

        # logging.basicConfig()
        sh_log = logging.getLogger().setLevel(logging.ERROR)  # silent index
        self.simhashIndex = SimhashIndex(
            objs, f=self.dimension, k=self.tolerance, log=sh_log
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
