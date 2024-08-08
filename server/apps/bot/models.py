import logging

from django.contrib.postgres.fields import ArrayField
from django.db import models

from server.apps.core.incident_types import IncidentType
from server.apps.core.models import Country

logger = logging.getLogger(__name__)


class Channel(models.Model):
    """
    List of channels that bot added to
    """

    channel_id = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return f"{self.channel_id}"

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"


class ChannelIncidentType(models.Model):
    """
    Model that connects channels + incident types
    and status field
    """

    channel = models.ForeignKey(
        Channel, on_delete=models.CASCADE, related_name="incident_types"
    )
    incident_type = models.ForeignKey(IncidentType, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.channel} - {self.incident_type}"

    class Meta:
        unique_together = ("channel", "incident_type")


class ChannelCountry(models.Model):
    """
    Connects (channels + incident types) and countries
    enabled_regions: list of regions id that enabled for this country
    status: field to turn conutry on and off
    """

    channel_incident_type = models.ForeignKey(
        ChannelIncidentType, on_delete=models.CASCADE, related_name="subscriptions"
    )
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    enabled_regions = ArrayField(
        models.CharField(max_length=16), blank=True, default=list
    )
    status = models.BooleanField(default=True)

    class Meta:
        unique_together = ("channel_incident_type", "country")

    def __str__(self):
        return f"{self.channel_incident_type} - {self.country}"
