from django.db.models.signals import post_save
from django.dispatch import receiver

from server.apps.bot.logic.send import send_message
from server.apps.bot.models import Channel, TypeStatus

from .models import MediaIncident


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
                if type_status.status:
                    send_message(chn.channel_id, msg)
            except Exception as e:
                print("An error occurred: ", e)
                print("instance: ", instance.id)
