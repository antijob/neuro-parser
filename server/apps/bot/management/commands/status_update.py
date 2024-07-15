from django.core.management.base import BaseCommand

from server.apps.bot.models import Channel, CountryStatus, RegionStatus, TypeStatus
from server.apps.core.models import IncidentType, Country, Region

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        all_channels = Channel.objects.all()
        for chn in all_channels:
            for incident in IncidentType.objects.all():
                if not TypeStatus.objects.filter(
                    incident_type=incident, channel=chn
                ).exists():
                    TypeStatus.objects.create(
                        incident_type=incident, channel=chn, status=True
                    )
            for country in Country.objects.all():
                if not CountryStatus.objects.filter(
                    country=country, channel=chn
                ).exists():
                    CountryStatus.objects.create(
                        country=country, channel=chn, status=True
                    )
            for region in Region.objects.all():
                if not RegionStatus.objects.filter(region=region, channel=chn).exists():
                    RegionStatus.objects.create(region=region, channel=chn, status=True)

        logger.info("All statuses created or already exists")
