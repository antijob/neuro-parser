from django.contrib import admin

from server.apps.bot.models import (
    Channel,
    TypeStatus
)
admin.site.register(Channel)

@admin.register(TypeStatus)
class TypeStatusAdmin(admin.ModelAdmin):
    list_display = ('incident_type', 'channel', 'status')

