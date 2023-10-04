# Module for checking if downloaded article is repost or very similar
# on articles that we already have.
# If so we mark it as
# is_downloaded = True
# is_duplicate = True
# And then we shouldn't count them futher
from datetime import datetime, timedelta
from difflib import SequenceMatcher

def latest_unique_articles():
    from server.apps.core.models import Article

    start_date = datetime.now().date() - timedelta(days=3)
    return Article.objects.filter(
        publication_date__gte=start_date, 
        is_duplicate=False, 
        is_downloaded=True
        )


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


# ToDo: remove this. It's only for test
def get_orig(article_text_to_check: str):
    from server.apps.core.models import Article
    import re

    if not article_text_to_check:
        return False, None

    articles = Article.objects.filter(is_duplicate=False, is_downloaded=True)
    for art in articles:
        if not art.text:
            continue
        text1 = re.sub(r'http\S+', '', article_text_to_check)
        text2 = re.sub(r'http\S+', '', art.text)
        ratio = calc_ratio(text1, text2)
        if ratio > 0.7:
            return True, art
    return False, None
