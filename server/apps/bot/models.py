from django.db import models


class Channel(models.Model):
    """
    Model for storing data about chanels for updates
    and settings for them
    """
    channel_id = models.CharField(max_length=32, blank=False, null=False, unique=True)
    cat_01 = models.BooleanField(verbose_name="Увольнения", default=True)
    cat_02 = models.BooleanField(verbose_name="Забастовки", default=True)
    cat_03 = models.BooleanField(verbose_name="Диверсии", default=True)
