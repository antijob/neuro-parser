from django.contrib import admin

from server.apps.bot.models import (
    Channel,
    TypeStatus,
    CountryStatus,
    RegionStatus,
)

admin.site.register(Channel)


@admin.register(TypeStatus)
class TypeStatusAdmin(admin.ModelAdmin):
    list_display = ("incident_type", "channel", "status")


@admin.register(CountryStatus)
class CountryStatusAdmin(admin.ModelAdmin):
    list_display = ("country", "channel", "status")


@admin.register(RegionStatus)
class RegionStatusAdmin(admin.ModelAdmin):
    list_display = ("region", "channel", "status")
