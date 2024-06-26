from .query_checker import RATIO_THRESHOLD, reindex_and_detect_duplicates
from .article_index import SIMHASH_DIMENSION, SIMHASH_TOLERANCE
from typing import List, Tuple
from datetime import datetime, timedelta

from server.apps.core.models import Article
from django.db.models import QuerySet


def test_simhash_parameters(
    query: QuerySet, params1: Tuple[int, int, float], params2: Tuple[int, int, float]
) -> None:

    global SIMHASH_DIMENSION
    global SIMHASH_TOLERANCE
    global RATIO_THRESHOLD

    SIMHASH_DIMENSION = params1[0]
    SIMHASH_TOLERANCE = params1[1]
    RATIO_THRESHOLD = params1[2]
    duplicates_set1 = set(reindex_and_detect_duplicates(query))

    SIMHASH_DIMENSION = params2[0]
    SIMHASH_TOLERANCE = params2[1]
    RATIO_THRESHOLD = params2[2]
    duplicates_set2 = set(reindex_and_detect_duplicates(query))

    only_in_first = duplicates_set1 - duplicates_set2
    only_in_second = duplicates_set2 - duplicates_set1

    print(f"Params: {params1}:")
    for url in only_in_first:
        print(url)

    print(f"\nParams: {params2}:")
    for url in only_in_second:
        print(url)


# Example usage:
params1 = (128, 8, 0.5)
params2 = (64, 4, 0.3)
query = Article.objects.filter(
    is_downloaded=True, create_date__gte=datetime.now().date() - timedelta(hours=3)
)

test_simhash_parameters(query, params1, params2)
