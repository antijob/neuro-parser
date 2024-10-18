import logging
import sys

from django.db.models.signals import post_save
from django.dispatch import receiver

from server.apps.bot.models import Channel
from server.apps.bot.services.country import create_settings

from .models import IncidentType

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


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
