from django.core.cache import cache
import logging
from simhash import Simhash, SimhashIndex
import re
from server.apps.core.models import Article
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

SIMHASH_INDEX_KEY_TEMPLATE = "simhash-index-{dim}-{tol}"
SIMHASH_DIMENSION = 128
SIMHASH_TOLERANCE = 8
SIMHASH_INDEX_TIMEOUT = 3600 * 3  # 3 hours
clear_text = re.compile(r"http\S+")  # remove links


def get_latest_unique_articles() -> list[Article]:
    try:
        start_date = datetime.now().date() - timedelta(days=3)
        articles = Article.objects.filter(
            is_downloaded=True,
            is_parsed=True,
            is_duplicate=False,
            create_date__gte=start_date,
        )
        return articles
    except Exception as e:
        logger.error(f"Error fetching latest unique articles: {e}")
        return []


def make_simhash_from_article(article: Article) -> Simhash:
    try:
        title = article.title if article.title else ""
        text = article.text if article.text else ""
        full_text = "\n".join([title, text])
        full_text = full_text.strip().lower()
        full_text = clear_text.sub("", full_text)
        return Simhash(full_text, f=SIMHASH_DIMENSION)
    except Exception as e:
        logger.error(f"Error creating Simhash from article {article.id}: {e}")
        return Simhash("")


def get_simhash_distance(url1: str, url2: str) -> int:
    try:
        art1 = Article.objects.get(url=url1)
        art2 = Article.objects.get(url=url2)
        sh1 = make_simhash_from_article(art1)
        sh2 = make_simhash_from_article(art2)
        return sh1.distance(sh2)
    except Article.DoesNotExist as e:
        logger.error(f"Article not found for URLs: {url1} or {url2}: {e}")
        return -1
    except Exception as e:
        logger.error(f"Error calculating Simhash distance between articles: {e}")
        return -1


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
        try:
            cachedIndex = cache.get(self.key)
            if cachedIndex is None:
                self.build_index()
            else:
                self.simhashIndex = cachedIndex
        except Exception as e:
            logger.error(f"Error loading Simhash index: {e}")

    def save(self) -> None:
        try:
            if self.simhashIndex:
                cache.set(self.key, self.simhashIndex, SIMHASH_INDEX_TIMEOUT)
        except Exception as e:
            logger.error(f"Error saving Simhash index to cache: {e}")

    def build_index(self) -> None:
        try:
            articles = get_latest_unique_articles()
            objs = [(art.url, make_simhash_from_article(art)) for art in articles]
            sh_log = logging.getLogger().setLevel(logging.ERROR)  # silent index
            self.simhashIndex = SimhashIndex(
                objs, f=self.dimension, k=self.tolerance, log=sh_log
            )
        except Exception as e:
            logger.error(f"Error building Simhash index: {e}")

    def get_neighbours(self, article: Article) -> list[str]:
        if not article.text:
            return []
        try:
            sh = make_simhash_from_article(article)
            return self.simhashIndex.get_near_dups(sh)
        except Exception as e:
            logger.error(f"Error getting neighbors for article {article.id}: {e}")
            return []

    def add(self, article: Article) -> None:
        if not article.text:
            return
        try:
            sh = make_simhash_from_article(article)
            self.simhashIndex.add(article.url, sh)
        except Exception as e:
            logger.error(f"Error adding article {article.id} to Simhash index: {e}")
