def disable_models(self, request, queryset):
    """
    Disable selected models
    """
    for obj in queryset:
        obj.is_active = False
        obj.save()
    self.message_user(request, f"{queryset.count()} models will be switched.")


disable_models.short_description = "Disable models"
