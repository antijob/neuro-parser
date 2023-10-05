from django.core.cache import cache
import logging
from simhash import Simhash, SimhashIndex
import re


SWIMHASH_INDEX_KEY = "simhash-index"
SIMHASH_INDEX_TIMEOUT = 3600 * 3 # 3 hours
clear_text = re.compile(r'http\S+') # remove links


def clear_simhash(text):
    text = clear_text.sub('', text)
    return Simhash(text)


def compare(url1, url2):
    from server.apps.core.models import Article
    text1 = Article.objects.get(url=url1).text
    text2 = Article.objects.get(url=url2).text
    sh1 = clear_simhash(text1)
    sh2 = clear_simhash(text2)
    return sh1.distance(sh2)


def get_index():
    return cache.get(SWIMHASH_INDEX_KEY)


def store_index(index):
    cache.set(SWIMHASH_INDEX_KEY, index, SIMHASH_INDEX_TIMEOUT)


def create_index(articles=[]):
    if articles and len(articles) > 0:
        # ToDo: check if text is empty
        objs = [(art.url, clear_simhash(art.text)) for art in articles]
    else:
        objs = []

    logging.basicConfig()
    sh_log = logging.getLogger().setLevel(logging.ERROR) # silent index
    return SimhashIndex(objs, k=10, log=sh_log)


def neighbours(art, index):
    if not art.text:
        return []
    sh = clear_simhash(art.text)
    return index.get_near_dups(sh)


def add(art, index):
    if not art.text:
        return
    sh = clear_simhash(art.text)
    index.add(art.url, sh)
