import logging
import sys
from dataclasses import dataclass
import re

from server.apps.bot.data.messages import NEW_INCIDENT_TEMPLATE, NEW_TG_INCIDENT_TEMPLATE
from server.apps.bot.models import Channel, ChannelCountry, ChannelIncidentType
from server.apps.core.models import MediaIncident
from django.db import models

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


@dataclass
class IncidentPostData:
    incident_id: str
    message: str
    channel_id_list: list[str]


def prepare_message(inc: MediaIncident) -> str:
    if inc.source.is_telethon:
        return NEW_TG_INCIDENT_TEMPLATE.format(
            cat=inc.incident_type.description.replace(" ", "_"),
            title=inc.title,
            country=inc.country,
            region=inc.region,
            source=inc.source.public_tg_channel_link,
            desc=(
                inc.description
                if len(inc.description) < 3000
                else inc.description[:3000] + "..."
            ),
            # Convert telehon adress to public telegram link
            url=re.sub(r"https://t\.me/c/(?:-?\d+)(/\d+.*)",
                       lambda m: f"{inc.source.public_tg_channel_link}{m.group(1)}", " ".join(inc.urls))
        )
    else:
        return NEW_INCIDENT_TEMPLATE.format(
            cat=inc.incident_type.description.replace(" ", "_"),
            title=inc.title,
            country=inc.country,
            region=inc.region,
            desc=(
                inc.description
                if len(inc.description) < 3000
                else inc.description[:3000] + "..."
            ),
            url=" ".join(inc.urls),
        )


def get_incident_post_data(inc: MediaIncident) -> IncidentPostData:
    """
    Checks settings for all channels
    Returns dataclass with
    - incident id to make downvote kb
    - msg to send
    - list of channel ids that pass checks
    """
    msg = prepare_message(inc)

    # Базовый запрос для каналов с активными настройками
    base_query = Channel.objects.filter(
        incident_types__incident_type=inc.incident_type,
        incident_types__status=True,
        incident_types__subscriptions__country=inc.country,
        incident_types__subscriptions__status=True
    )

    if inc.region:
        # Если есть регион, фильтруем по enabled_regions или "все регионы"
        region_query = base_query.filter(
            models.Q(
                incident_types__subscriptions__enabled_regions__icontains=inc.region.name
            ) | models.Q(
                incident_types__subscriptions__enabled_regions__icontains="ALL"
            )
        )
        channels = list(region_query.values_list(
            'channel_id', flat=True).distinct())
    else:
        # Если региона нет, берем все подходящие каналы
        channels = list(base_query.values_list(
            'channel_id', flat=True).distinct())

    logger.debug(f"Created list of chn id's to send msg: {channels}")

    return IncidentPostData(
        message=msg,
        incident_id=inc.id,
        channel_id_list=channels,
    )
