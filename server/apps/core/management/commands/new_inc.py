import logging
from datetime import date

from django.core.management.base import BaseCommand

from server.apps.core.models import IncidentType, MediaIncident, Country, Region, User, Article

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Creates and saves an instance of BaseIncident"

    def handle(self, *args, **kwargs):
        # Assuming the default country is Russia
        try:
            country = Country.objects.get(name="RUS")
        except Exception as e:
            logger.error(f"Failed to get the default country: {e}")
            return

        # Assuming there is a default region
        try:
            region = Region.objects.first()
        except Exception as e:
            logger.error(f"Failed to get the default region: {e}")
            return

        # Assuming there is a default incident type
        try:
            incident_type = IncidentType.objects.first()
        except Exception as e:
            logger.error(
                f"Failed to get the default incident type, check if there is at least one: {e}"
            )
            return

        # Assuming there is a default user
        try:
            user = User.objects.first()
        except Exception as e:
            logger.error(f"Failed to get the default user: {e}")
            return

        # Delete existing sample article and incident
        try:
            MediaIncident.objects.get(title="Sample Article Title").delete()
            Article.objects.get(url="https://example.com/sample-article").delete()
        except Exception as e:
            pass

        try:
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
        except Exception as e:
            logger.error(f"Failed to create an article: {e}")
            return

        try:
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
        except Exception as e:
            logger.error(f"Failed to create an incident: {e}")
            return

        logger.info(f"Successfully created and saved an incident: {media_incident}")
