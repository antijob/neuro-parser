import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from server.apps.bot.models import Channel, ChannelIncidentType, ChannelCountry
from server.apps.core.models import Country, IncidentType
from server.apps.bot.services.country import get_region_codes

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Updates or creates ChannelIncidentType and ChannelCountry for all channels"

    def handle(self, *args, **options):
        with transaction.atomic():
            all_channels = Channel.objects.all()
            result = (0, 0)
            for channel in all_channels:
                result = self.process_channel(channel)
                logger.info(
                    f"Created {result[0]} ChannelIncidentType and {result[1]} ChannelCountry for channel {channel}"
                )

        logger.info("All statuses created or updated successfully")

    def process_channel(self, channel):
        # Process IncidentTypes
        cit_created = 0
        cc_created = 0
        for incident_type in IncidentType.objects.all():
            channel_incident_type, created = ChannelIncidentType.objects.get_or_create(
                channel=channel, incident_type=incident_type, defaults={"status": True}
            )
            if created:
                cit_created += 1

            # Process Countries for each ChannelIncidentType
            for country in Country.objects.all():
                channel_country, created = ChannelCountry.objects.get_or_create(
                    channel_incident_type=channel_incident_type,
                    country=country,
                    defaults={
                        "status": True,
                        "enabled_regions": (get_region_codes(country)),
                    },
                )
                if created:
                    cc_created += 1

            return (cit_created, cc_created)
