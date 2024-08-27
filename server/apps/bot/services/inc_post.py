import logging
import sys
from typing import List

from asgiref.sync import sync_to_async

from server.apps.bot.bot_instance import get_bot
from server.apps.bot.models import Channel, ChannelCountry, ChannelIncidentType
from server.apps.core.data.messages import NEW_INCIDENT_TEMPLATE
from server.apps.core.models import MediaIncident

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


@sync_to_async
def get_all_channels() -> List[Channel]:
    return list(Channel.objects.all())


@sync_to_async
def get_channel_data(chn: Channel, inc: MediaIncident):
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


@sync_to_async
def prepare_message(inc: MediaIncident):
    return NEW_INCIDENT_TEMPLATE.format(
        cat=inc.incident_type.description,
        title=inc.title,
        country=inc.country,
        region=inc.region,
        desc=inc.description,
        url=" ".join(inc.urls),
    )


async def mediaincident_post(inc: MediaIncident):
    """
    using of function in sync context
    asyncio.run(mediaincident_post(incident))
    """
    try:
        all_channels = await get_all_channels()

        msg = await prepare_message(inc)

        async with get_bot() as bot:
            for chn in all_channels:
                try:
                    channel_incident, channel_country = await get_channel_data(chn, inc)
                    if channel_incident and channel_country:
                        if (
                            channel_incident.status
                            and channel_country.status
                            and inc.region.name in channel_country.enabled_regions
                        ):
                            await bot.send_message(text=msg, chat_id=chn.channel_id)
                            logger.info(f"Sent message to channel {chn.channel_id}")
                        else:
                            logger.info(
                                f"Skipping channel {chn.channel_id} due to status checks"
                            )
                    else:
                        logger.warning(f"No data for channel {chn.channel_id}")
                except Exception as e:
                    logger.error(f"Error processing channel {chn.channel_id}: {e}")

    except Exception as e:
        logger.error(f"Error in mediaincident_post: {e}", exc_info=True)
