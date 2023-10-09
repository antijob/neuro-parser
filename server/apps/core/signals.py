from django.db.models.signals import post_save
from django.dispatch import receiver
from server.apps.core.incident_types import IncidentType
from .models import MediaIncident
from server.apps.bot.models import Channel, TypeStatus
from server.apps.bot.logic.send import send_message

inc_template = """
New incident created
Title: {title}
Description: {desc}
Status: {status}
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
                                    title=instance.title,
                                    desc=instance.description,
                                    status=instance.status,
                                    url=instance.urls,
                                    )
        for chn in all_channels:
            type_status = TypeStatus.objects.get(channel=chn, incident_type=instance.incident_type)
            if type_status.status:
                send_message(chn.channel_id, msg)

