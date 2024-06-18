import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from server.apps.bot.logic.send import send_message
from server.apps.bot.models import Channel, CountryStatus, RegionStatus, TypeStatus

from .models import MediaIncident

logger = logging.getLogger(__name__)

inc_template = """
New incident created
Category: {cat}
Title: {title}
Description: {desc}
URLs: {url}
"""


@receiver(post_save, sender=MediaIncident)
def mediaincident_post_save(sender, instance, created, **kwargs):
    """
    Function that will be executed on each save of
    new instance of MediaIncident model
    """
    if created:
        all_channels = Channel.objects.all()
        msg = inc_template.format(
            cat=instance.incident_type.description,
            title=instance.title,
            desc=instance.description,
            url=" ".join(instance.urls),
        )
        for chn in all_channels:
            try:
                type_status = TypeStatus.objects.get(
                    channel=chn, incident_type=instance.incident_type
                )
                country_status = CountryStatus.objects.get(
                    channel=chn, country=instance.country
                )
                region_status = RegionStatus.objects.get(
                    channel=chn, region=instance.region
                )
                if (
                    type_status.status
                    and country_status.status
                    and region_status.status
                ):
                    send_message(chn.channel_id, msg)
            except Exception as e:
                logger.error(f"An error occurred: {e} \n (In instance: {instance.id})")
