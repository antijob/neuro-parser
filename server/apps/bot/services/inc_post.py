import logging
import sys
from dataclasses import dataclass


from server.apps.bot.data.messages import NEW_INCIDENT_TEMPLATE
from server.apps.bot.models import Channel, ChannelCountry, ChannelIncidentType
from server.apps.core.models import MediaIncident

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


@dataclass
class IncidentPostData:
    incident_id: str
    message: str
    channel_id_list: list[str]


def prepare_message(inc: MediaIncident) -> str:
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


def process_channel(chn, inc: MediaIncident) -> bool:
    """
    checks should we or not send a message to the given channel
    1. ch_inc and ch_country should exist
    2. they status field should be True
    3. if in the given inc exists region field
          it should be in ch_country enabled_regions list
    """
    channel_incident = ChannelIncidentType.objects.get(
        channel=chn, incident_type=inc.incident_type
    )

    channel_country = ChannelCountry.objects.get(
        channel_incident_type=channel_incident, country=inc.country
    )

    logger.debug(
        f"Processing chanel for sending msg: {channel_incident}, {channel_country}"
    )

    if not (channel_incident and channel_country):
        return False

    if not (channel_incident.status and channel_country.status):
        return False

    if inc.region:
        if inc.region.name not in channel_country.enabled_regions:
            return False
    return True


def get_incident_post_data(inc: MediaIncident) -> IncidentPostData:
    """
    Checks settings for all channels
    Returns dataclass with
    - incidint id to make downvote kb
    - msg to send
    - list of channel ids that pass checks
    """
    all_channels = list(Channel.objects.all())

    msg = prepare_message(inc)

    channels = []
    for chn in all_channels:
        if process_channel(chn, inc):
            channels.append(chn.channel_id)

    logger.debug(f"Created list of chn id's to send msg: {channels}")

    return IncidentPostData(
        message=msg,
        incident_id=inc.id,
        channel_id_list=channels,
    )
