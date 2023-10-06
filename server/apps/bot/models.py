from django.db import models
from server.apps.core.incident_types import IncidentType


class Channel(models.Model):
    """
    Model for storing data about chanels for updates
    """

    channel_id = models.CharField(max_length=32, blank=False, null=False, unique=True)
    type = models.ManyToManyField(IncidentType, through='TypeStatus')

    def __str__(self):
        return self.channel_id


class TypeStatus(models.Model):
    """
    Model that connects channels and incident types
    with additional status field
    """
    incident_type = models.ForeignKey(IncidentType, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)

