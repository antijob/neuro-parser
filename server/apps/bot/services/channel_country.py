from server.apps.core.models import Region
from server.apps.bot.models import ChannelCountry
import logging

logger = logging.getLogger(__name__)


def add_region(chn_country: ChannelCountry, region_code: str) -> None:
    if not Region.objects.filter(name=region_code).exists():
        logger.error(f"Region with code: {region_code} not found")
        return None
    if region_code in chn_country.enabled_regions:
        logger.error(f"Region with code: {region_code} already in list")
        return None
    chn_country.enabled_regions.append(region_code)
    chn_country.save()


def del_region(chn_country: ChannelCountry, region_code: str) -> None:
    if not Region.objects.filter(name=region_code).exists():
        logger.error(f"Region with code: {region_code} not found")
        return None
    if region_code not in chn_country.enabled_regions:
        logger.error(f"Region with code: {region_code} not found in list")
        return None
    chn_country.enabled_regions.remove(region_code)
    chn_country.save()
