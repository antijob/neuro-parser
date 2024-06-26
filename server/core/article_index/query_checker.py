from difflib import SequenceMatcher
from .article_index import ArticleIndex

from server.apps.core.models import Article
from django.db.models import QuerySet
from typing import List


RATIO_THRESHOLD = 0.5


def calc_ratio(a: str, b: str) -> float:
    a = a.lower()
    b = b.lower()
    match = SequenceMatcher(None, a, b)
    if match.get_matching_blocks():
        return match.ratio()
    return 0


def reindex_and_detect_duplicates(query: QuerySet) -> List[str]:
    articleIndex = ArticleIndex()
    articleIndex.load()

    duplicate_urls = []

    for article in query:
        if not article.text:
            duplicate_urls.append(article.url)
            continue

        neighbours = articleIndex.get_neighbours(article)

        if article.url not in neighbours:
            for n_article in Article.objects.filter(url__in=neighbours):
                if calc_ratio(n_article.text, article.text) >= RATIO_THRESHOLD:
                    duplicate_urls.append(article.url)
                    break

        if article.url not in duplicate_urls:
            articleIndex.add(article)

    articleIndex.save()

    return duplicate_urls


def mark_duplicates(query: QuerySet) -> None:
    duplicate_urls = reindex_and_detect_duplicates(query)
    duplicates_query = query.filter(url__in=duplicate_urls)
    duplicates_query.update(is_duplicate=True)
