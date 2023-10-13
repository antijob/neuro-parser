# Module for checking if downloaded article is repost or very similar
# on articles that we already have.
# If so we mark it as
# is_downloaded = True
# is_duplicate = True
# And then we shouldn't count them futher
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from . import simhash_index
from server.apps.core.models import Article


def latest_unique_articles():
    start_date = datetime.now().date() - timedelta(days=3)
    articles = Article.objects.filter(
        is_downloaded=True,
        is_parsed=False,
        create_date__gte=start_date)
    return articles


def calc_ratio(a: str, b: str):
    match = SequenceMatcher(None, a, b)
    if match.get_matching_blocks():
        sim_ratio = match.ratio()
        return match.ratio()
    return 0


def check_repost(article_text_to_check: str):
    '''
    returns True if found article that have similarity with given one
    on more than 70% and False otherwise
    '''

    if not article_text_to_check:
        return False

    articles = latest_unique_articles()
    for art in articles:
        if not art.text:
            continue
        ratio = calc_ratio(article_text_to_check, art.text)
        if ratio > 0.7:
            return True
    return False


def check_repost_query(query):
    from server.apps.core.models import Article
    index = simhash_index.get_index()
    if index is None:
        index_articles = latest_unique_articles()
        index = simhash_index.create_index(index_articles)

    for art in query:
        if not art.text:
            art.is_duplicate = True
            art.save()
            continue

        neighbours = simhash_index.neighbours(art, index)
        # only unique urls can be in index
        if art.url in neighbours:
            is_unique = True
        elif neighbours and len(neighbours) > 0:
            is_unique = False
            for url in neighbours:
                dist = simhash_index.compare(url, art.url)

                # check if close in simhash distance
                if dist < 4:
                    continue

                # check if close by calc ratio
                text = Article.objects.get(url=url).text
                if not text:
                    continue
                if calc_ratio(text, art.text) > .5:
                    continue

                # okay, you are unique
                is_unique = True
                simhash_index.add(art, index)
                break
        else:
            simhash_index.add(art, index)
            is_unique = True

        art.is_duplicate = not is_unique
        art.save()

    simhash_index.store_index(index)
