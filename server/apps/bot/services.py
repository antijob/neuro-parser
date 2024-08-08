import logging
from typing import List, Optional

from django.db import transaction

from server.apps.bot.models import (
    Channel,
    ChannelCountry,
    ChannelIncidentType,
    Country,
    Region,
)
from server.apps.core.incident_types import IncidentType

logger = logging.getLogger(__name__)


def has_region(country: Country) -> bool:
    """
    Return True if country has regions
    """
    return Region.objects.filter(country=country).exists()


def get_region_codes(country: Country) -> List[Optional[str]]:
    """
    Return list of regions codes
    if country has regions
    or empty list if not
    """
    regions = Region.objects.filter(country=country)
    if bool(regions):
        return [r.name for r in regions]
    else:
        return []


def create_settings(chn: Channel):
    """
    For given channel creates all possible
    options for incident types and countries
    ChannelIncidentType and ChannelCountry relatively
    for ChannelCountry also add regions
    should be used right after adding bot to new channel
    """
    with transaction.atomic():
        logger.info(f"Create settings for channel {chn}")
        channel_incident_types = []
        channel_countries = []
        for it in IncidentType.objects.all():
            cit = ChannelIncidentType(channel=chn, incident_type=it, status=True)
            channel_incident_types.append(cit)
            for c in Country.objects.all():
                cc = ChannelCountry(
                    channel_incident_type=cit,
                    country=c,
                    status=True,
                    enabled_regions=get_region_codes(c),
                )
                channel_countries.append(cc)
        ChannelIncidentType.objects.bulk_create(channel_incident_types)
        ChannelCountry.objects.bulk_create(channel_countries)
