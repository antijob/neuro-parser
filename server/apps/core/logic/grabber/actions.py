from django.conf import settings

from server.apps.core.models import Article, Source, Tag

from .duplicates import delete_duplicates


def update_sources():
    sources = Source.objects.filter(is_active=True)
    for source in sources:
        source.update()


def download_articles():
    for article in Article.objects.filter(is_downloaded=False):
        article.download()


def rate_articles():
    articles = Article.objects.filter(is_downloaded=True,
                                      relevance__isnull=True)
    for article in articles:
        article.rate_relevance()


def create_incidents():
    articles = Article.objects.filter(is_downloaded=True,
                                      is_incident_created=False,
                                      relevance__gte=settings.RELEVANCE_TRESHOLD)
    for article in articles:
        article.create_incident()


def apply_tags():
    tags = Tag.objects.filter(is_active=True)
    for tag in tags:
        tag.apply()


def grab_news():
    print("UPDATE SOURCES")
    update_sources()

    print("DOWNLOAD ART")
    download_articles()

    print("RATE ART")
    rate_articles()

    print("CREATE INC")
    create_incidents()

    print("APPLY TAGS")
    apply_tags()

    print("DELETE DUPES")
    delete_duplicates()

