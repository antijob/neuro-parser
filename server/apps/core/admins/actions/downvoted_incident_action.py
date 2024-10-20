def downvoted_incidents(self, request, queryset):
    """
    Downvote selected incidents
    """
    for obj in queryset:
        obj.downvote += 1
        obj.save()

    self.message_user(request, f"{queryset.count()} incidents were downvoted.")


downvoted_incidents.short_description = "Поставить низкую оценку инциденту"
