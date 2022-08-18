# -*- coding: utf-8 -*-

from django.contrib import admin  # noqa

from server.apps.users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name',)
