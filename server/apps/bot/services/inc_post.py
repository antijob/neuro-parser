import asyncio
import logging
import sys
from typing import Optional

from aiogram.exceptions import TelegramBadRequest
from asgiref.sync import sync_to_async

from server.apps.bot.bot_instance import get_bot
from server.apps.bot.models import Channel, ChannelCountry, ChannelIncidentType
from server.apps.bot.data.messages import NEW_INCIDENT_TEMPLATE
from server.apps.core.models import MediaIncident

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


@sync_to_async
def get_all_channels() -> list[Channel]:
    return list(Channel.objects.all())


@sync_to_async
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


@sync_to_async
def prepare_message(inc: MediaIncident) -> str:
    return NEW_INCIDENT_TEMPLATE.format(
        cat=inc.incident_type.description,
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


async def process_channel(bot, chn, inc: MediaIncident, msg: str) -> bool:
    try:
        channel_incident, channel_country = await get_channel_data(chn, inc)
        if not (channel_incident and channel_country):
            logger.warning(f"No data for channel {chn.channel_id}")
            return False

        if not (channel_incident.status and channel_country.status):
            logger.info(f"Skipping channel {chn.channel_id} due to status checks")
            return False

        if inc.region:
            if inc.region.name not in channel_country.enabled_regions:
                logger.info(f"Skipping channel {chn.channel_id} due to region mismatch")
                return False

        try:
            await bot.send_message(text=msg, chat_id=chn.channel_id)
        except TelegramBadRequest as e:
            logger.warning(f"Can't send message to channel {chn.channel_id}: {e}")
        logger.info(f"Sent message to channel {chn.channel_id}")
        return True
    except Exception as e:
        logger.error(f"Error processing channel {chn.channel_id}: {e}", exc_info=True)
        return False


async def post_incident(inc: MediaIncident):
    """
    Asynchronously post media incident to all relevant channels.

    Usage in sync context:
    asyncio.run(post_incident(incident))
    """
    logger.info(f"Starting post_incident for incident: {inc.id}")
    try:
        all_channels = await get_all_channels()
        logger.info(f"Retrieved {len(all_channels)} channels")

        msg = await prepare_message(inc)
        logger.info("Message prepared successfully")

        async with get_bot() as bot:
            tasks = [process_channel(bot, chn, inc, msg) for chn in all_channels]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            success_count = sum(1 for r in results if r is True)
            error_count = sum(1 for r in results if r is False)

            logger.info(
                f"Processed all channels. Successes: {success_count}, Errors: {error_count}"
            )
    except Exception as e:
        logger.error(f"Error in post_incident: {e}", exc_info=True)
        raise
