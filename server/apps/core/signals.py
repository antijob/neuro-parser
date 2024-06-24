import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from server.apps.bot.logic.send import send_message
from server.apps.bot.models import Channel, CountryStatus, RegionStatus, TypeStatus

from .models import MediaIncident, IncidentType

logger = logging.getLogger(__name__)

inc_template = """
New incident created
Category: {cat}
Title: {title}
Country: {country}
Region: {region}
Description: {desc}
URLs: {url}
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
                logger.error(f"An error occurred: {e} \nIn instance: {instance.id}")


@receiver(post_save, sender=IncidentType)
def incidenttype_post_save(sender, instance, created, **kwargs):
    """
    Executes on creation of new instance of IncidentType model
    Creates status (TypeStatus) for each channel in order to guarantee
    that message about new incident will be sent to users
    """
    if created:
        all_channels = Channel.objects.all()
        for chn in all_channels:
            try:
                TypeStatus.objects.create(
                    incident_type=instance, channel=chn, status=True
                )
            except Exception as e:
                logger.error(
                    f"An error in signal on creation TypeStatus: {e} \nInstance: {instance.id}"
                )
