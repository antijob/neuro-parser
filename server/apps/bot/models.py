from django.db import models
from server.apps.core.models import Country, Region, IncidentType


class Channel(models.Model):
    """
    Model for storing data about chanels for updates
    """

    channel_id = models.CharField(max_length=32, blank=False, null=False, unique=True)
    type = models.ManyToManyField(IncidentType, through="TypeStatus")
    country = models.ManyToManyField(Country, through="CountryStatus")
    region = models.ManyToManyField(Region, through="RegionStatus")

    def save(self, *args, **kwargs):
        is_new = self.pk = None
        print("SAVED")
        super().save(*args, **kwargs)

        if is_new:
            print("GOING FOR status")
            for country in Country.objects.all().exclude(name="ALL"):
                CountryStatus.objects.create(country=country, channel=self, status=True)
            for region in self.region.all().exclude(name="ALL"):
                RegionStatus.objects.create(region=region, channel=self, status=True)

    def __str__(self):
        return f"{self.channel_id}"

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"


class TypeStatus(models.Model):
    """
    Model that connects channels and incident types
    with additional status field
    """

    incident_type = models.ForeignKey(IncidentType, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)


class CountryStatus(models.Model):
    """
    Model that connects channels and countries
    with additional status field
    """

    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)


class RegionStatus(models.Model):
    """
    Model that connects channels and regions
    with additional status field
    """

    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
