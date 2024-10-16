import logging
import sys

from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver

from server.apps.bot.bot_instance import bot, close_bot
from server.apps.bot.models import Channel, ChannelCountry, ChannelIncidentType
from server.apps.bot.services.country import create_settings
from server.apps.core.data.messages import NEW_INCIDENT_TEMPLATE

from .models import IncidentType, MediaIncident

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


@receiver(post_save, sender=MediaIncident)
def mediaincident_post_save(sender, instance, created, **kwargs):
    """
    Function that will be executed on creation of
    new instance of MediaIncident model
    It checks if all statuses are true and if so sends message to th channel
    """
    if not created:
        return

    all_channels = Channel.objects.all()
    msg = NEW_INCIDENT_TEMPLATE.format(
        cat=instance.incident_type.description,
        title=instance.title,
        country=instance.country,
        region=instance.region,
        desc=instance.description,
        url=" ".join(instance.urls),
    )
    for chn in all_channels:
        try:
            channel_incident = ChannelIncidentType.objects.get(
                channel=chn, incident_type=instance.incident_type
            )
        except Exception as e:
            logger.error(
                f"Missing ChannelIncidentType {instance.id} for channel {channel.id}"
            )
            return None
        try:
            channel_country = ChannelCountry.objects.get(
                channel_incident_type=channel_incident, country=instance.country
            )
        except Exception as e:
            logger.error(f"Can't gent ChannelCountry: {e} For instance: {instance.id}")

        if (
            channel_incident.status
            and channel_country.status
            and instance.region.name in channel_country.enabled_regions
        ):
            try:
                async_to_sync(bot.send_message)(text=msg, chat_id=chn.channel_id)
            except Exception as e:
                logger.error(f"Failed to send message to channel {chn.channel_id}: {e}")
        else:
            logger.debug(f"Skipping channel {chn.channel_id} due to status checks")
            # logger.debug(f"Incident type status: {channel_incident.status}")
            # logger.debug(f"Country status: {channel_country.status}")
            # logger.debug(
            #     f"Region status: {instance.region.name in channel_country.enabled_regions}"
            # )
    async_to_sync(close_bot)()


@receiver(post_save, sender=IncidentType)
def incidenttype_post_save(sender, instance, created, **kwargs):
    """
    Executes on creation of new instance of IncidentType model
    and craetes settings for all channels with that incident type
    """
    if created:
        all_channels = Channel.objects.all()
        for chn in all_channels:
            try:
                create_settings(chn)
            except Exception as e:
                logger.error(
                    f"An error in signal on creation TypeStatus: {e} \nInstance: {instance.id}"
                )
