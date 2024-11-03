import logging
import sys
from dataclasses import dataclass
from typing import Optional


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


def get_all_channels() -> list[Channel]:
    return list(Channel.objects.all())


def get_channel_data(
    chn: Channel, inc: MediaIncident
) -> tuple[Optional[ChannelIncidentType], Optional[ChannelCountry]]:
    try:
        channel_incident = ChannelIncidentType.objects.get(
            channel=chn, incident_type=inc.incident_type
        )
        channel_country = ChannelCountry.objects.get(
            channel_incident_type=channel_incident, country=inc.country
        )
        return channel_incident, channel_country
    except Exception as e:
        logger.error(f"Error getting channel data: {e}")
        return None, None


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


def process_channel(chn, inc: MediaIncident, msg: str) -> bool:
    channel_incident, channel_country = get_channel_data(chn, inc)
    if not (channel_incident and channel_country):
        return False

    if not (channel_incident.status and channel_country.status):
        return False

    if inc.region:
        if inc.region.name not in channel_country.enabled_regions:
            return False
    return True

    # try:
    #     send_message_to_channels.delay(msg, chn.channel_id, inc_id=inc.id)
    # except TelegramBadRequest as e:
    #     error_traceback = traceback.format_exc()
    #     return PostingResult(
    #         succes=False,
    #         channel_id=chn,
    #         error_type=type(e).__name__,
    #         error_message=str(e),
    #         error_traceback=error_traceback,
    #     )
    #


def get_incident_post_data(inc: MediaIncident) -> IncidentPostData:
    """
    Checks settings for all channels
    Returns dataclass with
    - incidint id to make downvote kb
    - msg to send
    - list of channel ids that pass checks
    """
    all_channels = get_all_channels()

    msg = prepare_message(inc)

    channels = []
    for chn in all_channels:
        if process_channel(chn, inc, msg):
            channels.append(chn.channel_id)

    return IncidentPostData(
        message=msg,
        incident_id=inc.id,
        channel_id_list=channels,
    )
