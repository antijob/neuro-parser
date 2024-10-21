def deactivate_source(self, request, queryset):
    """
    Deactivate selected sources
    """
    for obj in queryset:
        obj.is_active = False
        obj.save()
    self.message_user(request, f"{queryset.count()} sources were deactivate.")


deactivate_source.short_description = "Deactivate sources"
