def activate_source(self, request, queryset):
    """
    Activate selected sources
    """
    for obj in queryset:
        obj.is_active = True
        obj.save()
    self.message_user(request, f"{queryset.count()} sources were activate.")

    activate_source.short_description = "Activate sources"
