# -*- coding: utf-8 -*-

from django.urls import path

from server.apps.core import views

urlpatterns = [
    path('grabber/algorithms/', views.GrabberAlogrithmsView.as_view(),
         name='grabber-algorithms'),
    path('grabber/algorithms_data/', views.GrabberAlgorithmsDataView.as_view(),
         name='grabber-algorithms-data'),
    path('grabber/source_statistics/',
         views.GrabberSourceStatisticsView.as_view(),
         name='grabber-source-statistics')
]

app_name = 'core'
