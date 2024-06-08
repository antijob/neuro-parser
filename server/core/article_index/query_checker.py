from difflib import SequenceMatcher
from .article_index import ArticleIndex

from server.apps.core.models import Article
from django.db.models import QuerySet


def calc_ratio(a: str, b: str) -> float:
    a = a.lower()
    b = b.lower()
    match = SequenceMatcher(None, a, b)
    if match.get_matching_blocks():
        return match.ratio()
    return 0


def check_repost_query(query: QuerySet):
    articleIndex = ArticleIndex()
    articleIndex.load()

    for article in query:
        if not article.text:
            article.is_duplicate = True
            article.save()
            continue

        neighbours = articleIndex.get_neighbours(
            article,
            distance=4,
        )

        is_duplicate = False
        if article.url not in neighbours:
            for n_article in Article.objects.filter(url__in=neighbours):
                if calc_ratio(n_article.text, article.text) < 0.5:
                    continue
                is_duplicate = True
                break

        if not is_duplicate:
            articleIndex.add(article)

        article.is_duplicate = is_duplicate
        article.save()

    articleIndex.save()
