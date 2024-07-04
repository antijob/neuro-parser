import logging
import sys

from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver

from server.apps.bot.bot_instance import bot, close_bot
from server.apps.bot.models import Channel, ChannelIncidentType

from .models import IncidentType, MediaIncident

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

inc_template = """
<b>Category:</b> {cat}
<b>Title:</b> {title}
<b>Country:</b> {country}
<b>Region:</b> {region}
<b>Description:</b> {desc}
<b>URLs:</b> {url}
"""


@receiver(post_save, sender=MediaIncident)
def mediaincident_post_save(sender, instance, created, **kwargs):
    """
    Function that will be executed on creation of
    new instance of MediaIncident model
    It checks if all statuses are true and if so sends message
    with bot
    """
    if created:
        all_channels = Channel.objects.all()
        msg = inc_template.format(
            cat=instance.incident_type.description,
            title=instance.title,
            country=instance.country,
            region=instance.region,
            desc=instance.description,
            url=" ".join(instance.urls),
        )
        for chn in all_channels:
            try:
                type_status = ChannelIncidentType.objects.get(
                    channel=chn, incident_type=instance.incident_type
                )
                logger.debug(
                    f"Chanel_IncidentType: {type_status.channel} {type_status.incident_type} {type_status.status}"
                )
                if type_status.status:
                    logger.info(f"Sending message to channel: {chn.channel_id}")
                    async_to_sync(bot.send_message)(chat_id=chn.channel_id, text=msg)

            except Exception as e:
                logger.error(f"An error occurred: {e} In instance: {instance.id}")
        logger.info("Message sent to all channels")
        async_to_sync(close_bot)()


@receiver(post_save, sender=IncidentType)
def incidenttype_post_save(sender, instance, created, **kwargs):
    # TODO: rewrite
    """
    Executes on creation of new instance of IncidentType model
    Creates status (TypeStatus) for each channel in order to guarantee
    that message about new incident will be sent to users
    """
    if created:
        all_channels = Channel.objects.all()
        for chn in all_channels:
            try:
                ChannelIncidentType.objects.create(
                    incident_type=instance, channel=chn, status=True
                )
            except Exception as e:
                logger.error(
                    f"An error in signal on creation TypeStatus: {e} \nInstance: {instance.id}"
                )
