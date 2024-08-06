from difflib import SequenceMatcher
from .article_index import ArticleIndex

from server.apps.core.models import Article
from django.db.models import QuerySet


RATIO_THRESHOLD = 0.5


def calc_ratio(a: str, b: str) -> float:
    a = a.lower()
    b = b.lower()
    match = SequenceMatcher(None, a, b)
    if match.get_matching_blocks():
        return match.ratio()
    return 0


def mark_duplicates(query: QuerySet) -> None:
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
                if not n_article.text:
                    continue

                if calc_ratio(n_article.text, article.text) >= RATIO_THRESHOLD:
                    duplicate_urls.append(article.url)
                    article.is_duplicate = True
                    article.duplicate_url = n_article.url
                    article.save()
                    break

        if article.url not in duplicate_urls:
            articleIndex.add(article)

    articleIndex.save()
