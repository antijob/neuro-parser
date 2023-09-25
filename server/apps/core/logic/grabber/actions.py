from django.conf import settings

from server.apps.core.models import Article, Source

from .duplicates import delete_duplicates
from .fetcher import Fetcher


def update_sources():
    sources = Source.objects.filter(is_active=True)
    for source in sources:
        try:
            source.update()
        except Exception as e:
            print(f"An error occurred while updating source: {e}")

def download_articles():
    for article in Article.objects.filter(is_downloaded=False):
        try:
            article.download()
        except Exception as e:
            print(f"An error occurred while downloading article: {e}")

def fetch_sources():
    fetcher = Fetcher()
    sources = Source.objects.filter(is_active=True)
    for source in sources:
        articles = Article.objects.filter(source=source, is_downloaded=False)
        fetcher.add_coroutine(source, articles)
    fetcher.await_all_coroutines()


def create_incidents():
    articles = Article.objects.filter(is_downloaded=True, is_incident_created=False)
    for article in articles:
        try:
            article.create_incident()
        except Exception as e:
            print(f"An error occurred while creating incident for article: {e}")


def grab_news():
    print("UPDATE SOURCES")
    update_sources()

    print("DOWNLOAD ART")
    fetch_sources()


def process_news():
    print("DELETE INCIDENT DUPES")
    delete_duplicates()

    print("CREATE INC")
    create_incidents()

