def enable_models(self, request, queryset):
    """
    Enable selected models
    """
    for obj in queryset:
        obj.is_active = True
        obj.save()
    self.message_user(request, f"{queryset.count()} models will be switched.")


enable_models.short_description = "Enable models"
