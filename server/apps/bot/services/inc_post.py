import logging
import asyncio
import sys

from asgiref.sync import async_to_sync

from server.apps.core.models import MediaIncident
from server.apps.bot.bot_instance import bot, close_bot
from server.apps.bot.models import Channel, ChannelCountry, ChannelIncidentType
from server.apps.core.data.messages import NEW_INCIDENT_TEMPLATE

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


def mediaincident_post(inc: MediaIncident):
    """
    Function that will be executed on creation of
    new instance of MediaIncident model
    It checks if all statuses are true and if so sends message to the channel
    """

    all_channels = Channel.objects.all()
    msg = NEW_INCIDENT_TEMPLATE.format(
        cat=inc.incident_type.description,
        title=inc.title,
        country=inc.country,
        region=inc.region,
        desc=inc.description,
        url=" ".join(inc.urls),
    )
    for chn in all_channels:
        try:
            channel_incident = ChannelIncidentType.objects.get(
                channel=chn, incident_type=inc.incident_type
            )
        except Exception as e:
            logger.error(f"Can't get ChannelIncidentType: {e} For instance: {inc.id}")
            return None
        try:
            channel_country = ChannelCountry.objects.get(
                channel_incident_type=channel_incident, country=inc.country
            )
        except Exception as e:
            logger.error(f"Can't gent ChannelCountry: {e} For instance: {inc.id}")

        if (
            channel_incident.status
            and channel_country.status
            and inc.region.name in channel_country.enabled_regions
        ):
            try:
                async_to_sync(bot.send_message)(text=msg, chat_id=chn.channel_id)
            except Exception as e:
                logger.error(f"Failed to send message to channel {chn.channel_id}: {e}")
        else:
            logger.info(f"Skipping channel {chn.channel_id} due to status checks")

    async def async_sleep_and_close():
        await asyncio.sleep(2)
        await close_bot()

    async_to_sync(async_sleep_and_close)()
