import asyncio
import logging
import sys

from asgiref.sync import sync_to_async

from server.apps.bot.bot_instance import get_bot
from server.apps.bot.models import Channel, ChannelCountry, ChannelIncidentType
from server.apps.core.data.messages import NEW_INCIDENT_TEMPLATE
from server.apps.core.models import MediaIncident

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


@sync_to_async
def get_channel_data(chn, inc):
    channel_incident = None
    channel_country = None
    try:
        channel_incident = ChannelIncidentType.objects.get(
            channel=chn, incident_type=inc.incident_type
        )
        channel_country = ChannelCountry.objects.get(
            channel_incident_type=channel_incident, country=inc.country
        )
    except Exception as e:
        logger.error(f"Error getting channel data: {e}")
    return channel_incident, channel_country


async def mediaincident_post(inc: MediaIncident):
    try:
        all_channels = await sync_to_async(list)(Channel.objects.all())
    except Exception as e:
        logger.error(f"Error getting channels: {e}")

    msg = NEW_INCIDENT_TEMPLATE.format(
        cat=inc.incident_type.description,
        title=inc.title,
        country=inc.country,
        region=inc.region,
        desc=inc.description,
        url=" ".join(inc.urls),
    )

    async def send_to_channel(chn):
        try:
            channel_incident, channel_country = await get_channel_data(chn, inc)

            if (
                channel_incident.status
                and channel_country.status
                and inc.region.name in channel_country.enabled_regions
            ):

                async with get_bot() as bot:
                    await bot.send_message(text=msg, chat_id=chn.channel_id)
            else:
                logger.info(f"Skipping channel {chn.channel_id} due to status checks")
        except Exception as e:
            logger.error(f"Error processing channel {chn.channel_id}: {e}")

    await asyncio.gather(*[send_to_channel(chn) for chn in all_channels])
