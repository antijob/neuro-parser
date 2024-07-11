import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from server.apps.bot.models import Channel, ChannelIncidentType, ChannelCountry
from server.apps.core.incident_types import IncidentType
from server.apps.core.models import Country, Region

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Updates or creates ChannelIncidentType and ChannelCountry for all channels"

    def handle(self, *args, **options):
        with transaction.atomic():
            all_channels = Channel.objects.all()
            for channel in all_channels:
                self.process_channel(channel)

        logger.info("All statuses created or updated successfully")

    def process_channel(self, channel):
        # Process IncidentTypes
        for incident_type in IncidentType.objects.all():
            channel_incident_type, created = ChannelIncidentType.objects.get_or_create(
                channel=channel, incident_type=incident_type, defaults={"status": True}
            )
            if created:
                logger.info(
                    f"Created ChannelIncidentType for channel {channel.channel_id} and incident type {incident_type}"
                )

            # Process Countries for each ChannelIncidentType
            for country in Country.objects.all():
                channel_country, created = ChannelCountry.objects.get_or_create(
                    channel_incident_type=channel_incident_type,
                    country=country,
                    defaults={
                        "status": True,
                        "enabled_regions": (
                            country.get_region_codes() if country.has_region() else []
                        ),
                    },
                )
                if created:
                    logger.info(
                        f"Created ChannelCountry for channel {channel.channel_id}, incident type {incident_type}, and country {country}"
                    )
