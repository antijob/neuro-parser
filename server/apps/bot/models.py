from django.db import models, transaction
from server.apps.core.incident_types import IncidentType
from server.apps.core.models import Country, Region
from django.contrib.postgres.fields import ArrayField


class Channel(models.Model):
    """
    List of channels to send incidents
    on save: add all possible options for incident types and countries
    """

    channel_id = models.CharField(max_length=32, unique=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        with transaction.atomic():
            super().save(*args, **kwargs)
            if is_new:
                channel_incident_types = []
                channel_countries = []
                for it in IncidentType.objects.all():
                    cit = ChannelIncidentType(
                        channel=self, incident_type=it, status=True
                    )
                    channel_incident_types.append(cit)
                    for c in Country.objects.all():
                        cc = ChannelCountry(
                            channel_incident_type=cit,
                            country=c,
                            status=True,
                        )
                        channel_countries.append(cc)
            ChannelIncidentType.objects.bulk_create(channel_incident_types)
            ChannelCountry.objects.bulk_create(channel_countries)

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
    enabled_regions = ArrayField(models.IntegerField(), blank=True, default=list)
    status = models.BooleanField(default=True)

    class Meta:
        unique_together = ("channel_incident_type", "country")

    def __str__(self):
        return f"{self.channel_incident_type} - {self.country}"
