from server.apps.core.logic.morphy import normalize_text
from server.apps.core.models import Source


def rate_text(normalized_text):
    rates = {}
    for algorithm_name, algorithm in Source.ALGORITHMS_MAP.items():
        rates[algorithm_name] = int(algorithm.rate(normalized_text))
    return rates


def rate_articles(articles):
    data = []
    for article in articles:
        normalized_text = normalize_text(article.text)
        rates = rate_text(normalized_text)
        rates['title'] = article.title
        rates['url'] = article.url
        data += [rates]
    return data
