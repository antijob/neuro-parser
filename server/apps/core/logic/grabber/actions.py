from django.conf import settings

from server.apps.core.models import Article, Source

from .duplicates import delete_duplicates


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
    download_articles()

    print("CREATE INC")
    create_incidents()

    print("DELETE INCIDENT DUPES")
    delete_duplicates()

