import os.path
from navec import Navec
from slovnet import NER

from django.conf import settings
from django.utils import timezone

from server.apps.core.logic.morphy import normalize_text
from server.apps.core.models import Article, MediaIncident


MIN_TERMS_COUNT = 4
MIN_INTERSECTION_LENGTH = 3
SIMILARITY_PERCENT = 34
VALUABLE_TEXT_SIZE = 3000

DATA_DIR = os.path.join(
    settings.BASE_DIR,
    'server', 'apps', 'core', 'logic', 'grabber', 'classificator', 'data')
navec = Navec.load(os.path.join(DATA_DIR,
                                'navec_news_v1_1B_250K_300d_100q.tar'))
ner = NER.load(os.path.join(DATA_DIR, 'slovnet_ner_news_v1.tar'))
ner.navec(navec)


def extract_terms(text):
    markup = ner(text)
    terms = {tuple(normalize_text(text[span.start: span.stop]))
             for span in markup.spans}
    return terms


def are_similar_sets(s1, s2):
    intersection = s1 & s2
    if len(intersection) < MIN_INTERSECTION_LENGTH:
        return False
    shortest_set = min((s1, s2), key=lambda x: len(x))
    overlap = len(intersection) / len(shortest_set) * 100
    return overlap >= SIMILARITY_PERCENT


def add_terms_to_articles(articles, save=False):
    for article in articles:
        if not article.terms:
            article.terms = list(extract_terms(article.text))
            if save:
                article.save(update_fields=['terms'])
    return articles


def compare_articles_terms(articles_with_terms):
    duplicates = {}
    articles_with_terms = list(articles_with_terms)
    for index, article_a in enumerate(articles_with_terms[:-1]):
        if article_a.incident.status == MediaIncident.DELETED:
            continue
        article_duplicates = []
        if len(article_a.terms) < MIN_TERMS_COUNT:
            continue
        for article_b in articles_with_terms[index + 1:]:
            if article_a.source and article_a.source == article_b.source:
                continue
            if article_a.url == article_b.url:
                continue
            if len(article_b.terms) < MIN_TERMS_COUNT:
                continue
            if are_similar_sets(set(article_a.terms), set(article_b.terms)):
                article_duplicates += [article_b]
        if article_duplicates:
            duplicates[article_a] = article_duplicates
    return duplicates


def todays_articles():
    start_date = timezone.now().date() - timezone.timedelta(days=1)
    return Article.objects.filter(publication_date__gte=start_date,
                                  is_incident_created=True,
                                  incident__isnull=False,
                                  incident__status=MediaIncident.UNPROCESSED)


def delete_duplicated_incidents(duplicates):
    for article, article_duplicates in duplicates.items():
        for duplicate in article_duplicates:
            duplicate.incident.status = MediaIncident.DELETED
            title = duplicate.incident.any_title()
            if not title.startswith("[Дубликат]"):
                title = '[Дубликат] ' + title
            duplicate.incident.public_title = title
            duplicate.incident.duplicate = article.incident
            duplicate.incident.save(update_fields=['status',
                                                   'duplicate',
                                                   'public_title',
                                                   'public_description'])
            article.incident.urls = (article.incident.urls +
                                     duplicate.incident.urls)
        article.incident.save(update_fields=['urls'])


def delete_duplicates():
    articles = todays_articles()
    articles_with_terms = add_terms_to_articles(articles)
    duplicates = compare_articles_terms(articles_with_terms)
    delete_duplicated_incidents(duplicates)


def search_duplicates_in_history(articles, history):
    articles_with_terms = add_terms_to_articles(articles, save=True)
    duplicates = {}
    for old_article in history:
        if not old_article.terms:
            add_terms_to_articles([old_article], save=True)
            if not old_article.terms:
                continue
        for article in articles_with_terms:
            if article.id == old_article.id:
                continue
            s1 = set(article.terms or [])
            s2 = set(old_article.terms or [])
            if are_similar_sets(s1, s2):
                duplicates[article] = duplicates.get(article, []) + [old_article]
    delete_duplicated_incidents(duplicates)
