# -*- coding: utf-8 -*-

from django.urls import path

from server.apps.analytics import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
]

app_name = "analytics"
