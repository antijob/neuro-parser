import logging
from datetime import date

from django.core.management.base import BaseCommand

from server.apps.core.models import (
    IncidentType,
    MediaIncident,
    Country,
    Region,
    User,
    Article,
)
from server.apps.bot.services.inc_post import mediaincident_post

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Creates and saves an instance of MediaIncident"

    def handle(self, *args, **kwargs):
        # Проверка и удаление существующего медиа инцидента
        try:
            existing_incident = MediaIncident.objects.get(title="Sample Article Title")
            if existing_incident:
                logger.info(
                    f"Media Incident with title 'Sample Article Title' already exists. Deleting the existing incident."
                )
                existing_incident.delete()
        except MediaIncident.DoesNotExist:
            logger.info(
                f"No existing media incident found with title 'Sample Article Title'. Proceeding to create a new one."
            )
        except Exception as e:
            logger.error(
                f"An error occurred while checking for existing media incidents: {e}"
            )
            return

        # Проверка и удаление существующей статьи
        try:
            existing_article = Article.objects.get(
                url="https://example.com/sample-article"
            )
            if existing_article:
                logger.info(
                    f"Article with URL 'https://example.com/sample-article' already exists. Deleting the existing article."
                )
                existing_article.delete()
        except Article.DoesNotExist:
            logger.info(
                f"No existing article found with URL 'https://example.com/sample-article'. Proceeding to create a new one."
            )
        except Exception as e:
            logger.error(f"An error occurred while checking for existing articles: {e}")
            return

        # Получение страны по умолчанию
        try:
            country = Country.objects.get(name="RUS")
        except Exception as e:
            logger.error(f"Failed to get the default country: {e}")
            return

        # Получение региона по умолчанию
        try:
            region = Region.objects.last()
        except Exception as e:
            logger.error(f"Failed to get the default region: {e}")
            return

        # Получение типа инцидента по умолчанию
        try:
            incident_type = IncidentType.objects.first()
        except Exception as e:
            logger.error(f"Failed to get the default incident type: {e}")
            return

        # Получение пользователя по умолчанию
        try:
            user = User.objects.first()
        except Exception as e:
            logger.error(f"Failed to get the default user: {e}")
            return

        # Создание статьи
        try:
            article = Article.objects.create(
                source=None,  # Или существующий источник
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
            logger.info(f"Created an article: {article}")
            logger.info(f"Created an article: {article.text}")
        except Exception as e:
            logger.error(f"Failed to create an article: {e}")
            return

        # Создание медиа инцидента
        # Проверка статьи
        if article is None:
            logger.error("Article object is None, cannot create MediaIncident.")
            return

        # Проверка пользователя
        if user is None:
            logger.error("User object is None, cannot create MediaIncident.")
            return

        # Проверка страны
        if country is None:
            logger.error("Country object is None, cannot create MediaIncident.")
            return

        # Проверка региона
        if region is None:
            logger.error("Region object is None, cannot create MediaIncident.")
            return

        # Проверка типа инцидента
        if incident_type is None:
            logger.error("IncidentType object is None, cannot create MediaIncident.")
            return

        try:
            logger.info(f"Creating an incident for article: {article}")
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
            # media_incident.save()
        except Exception as e:
            logger.error(f"Failed to create an incident: {e}")
            return

        logger.info(
            f"Successfully created and saved a media incident: {media_incident}"
        )

        # send a message to the channel
        try:
            mediaincident_post(media_incident)
        except Exception as e:
            logger.error(f"Failed to send a message to the channel: {e}")
