import logging
from datetime import date

from django.core.management.base import BaseCommand

from server.apps.core.incident_types import IncidentType
from server.apps.core.models import MediaIncident, Country, Region, User, Article

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Creates and saves an instance of BaseIncident"

    def handle(self, *args, **kwargs):
        # Assuming the default country is Russia
        country = Country.objects.get(name="RUS")

        # Assuming there is a default region
        region = Region.objects.first()

        # Assuming there is a default incident type
        incident_type = IncidentType.objects.first()

        # Assuming there is a default user
        user = User.objects.first()

        article = Article.objects.first()

        article = Article.objects.create(
            source=None,  # Or an existing source instance
            url="https://example.com/sample-article",
            title="Sample Article Title",
            text="This is a sample article text used for creating a media incident.",
            is_downloaded=True,
            is_parsed=True,
            is_incident_created=False,
            is_duplicate=False,
            rate={},
            create_date=date.today(),
            publication_date=date.today(),
        )

        media_incident = MediaIncident.objects.create(
            title=article.title,
            description=article.text,
            status=MediaIncident.UNPROCESSED,
            create_date=article.publication_date or date.today(),
            update_date=date.today(),
            assigned_to=user,
            related_article=article,
            country=country,
            region=region,
            incident_type=incident_type,
            count=1,
            urls=[article.url],
            public_title=article.title,
            public_description=article.text,
        )

        media_incident.save()

        logger.info(f"Successfully created and saved an incident: {media_incident}")
