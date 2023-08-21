# -*- coding: utf-8 -*-

from django.urls import path

from server.apps.core import views

urlpatterns = [
    # Dashboard views
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/incidents/', views.DashboardIncidentsView.as_view(), name='dashboard-incidents'),
    path('dashboard/userincidents/', views.DashboardUserIncidentsView.as_view(), name='dashboard-userincidents'),
    path('dashboard/mediaincidents/', views.DashboardMediaIncidentsView.as_view(), name='dashboard-mediaincidents'),
    path('dashboard/incidents/processed/', views.DashboardProcessedIncidentsView.as_view(), name='dashboard-incidents-processed'),
    path('dashboard/incidents/unprocessed/', views.DashboardUnprocessedIncidentsView.as_view(), name='dashboard-incidents-unprocessed'),
    path('dashboard/userincidents/unprocessed/', views.DashboardUnprocessedUserIncidentsView.as_view(), name='dashboard-userincidents-unprocessed'),
    path('dashboard/userincidents/rejected/', views.DashboardRejectedUserIncidentsView.as_view(), name='dashboard-userincidents-rejected'),
    path('dashboard/mediaincidents/rejected/', views.DashboardRejectedMediaIncidentsView.as_view(), name='dashboard-mediaincidents-rejected'),
    path('dashboard/userincidents/accepted/', views.DashboardAcceptedUserIncidentsView.as_view(), name='dashboard-userincidents-accepted'),
    path('dashboard/mediaincidents/accepted/', views.DashboardAcceptedMediaIncidentsView.as_view(), name='dashboard-mediaincidents-accepted'),
    path('dashboard/mediaincidents/unprocessed/', views.DashboardUnprocessedMediaIncidentsView.as_view(), name='dashboard-mediaincidents-unprocessed'),
    path('dashboard/incidents/assigned/', views.DashboardAssignedIncidentsView.as_view(), name='dashboard-incidents-assigned'),
    path('dashboard/incidents/in_progress/', views.DashboardInProgressUserIncidentsView.as_view(), name='dashboard-incidents-in-progress'),
    path('dashboard/incidents/data/', views.DashboardIncidentsTableDataView.as_view(), name='dashboard-incidents-data'),

    # Dashboard incident views
    path('dashboard/incident/create/', views.DashboardIncidentCreateView.as_view(),
         name='dashboard-incident-create'),
    path('dashboard/incident/<int:pk>/update/', views.DashboardIncidentUpdateView.as_view(),
         name='dashboard-incident-update'),
    path('dashboard/incident/<int:pk>/ajax/', views.UserIncidentAjaxUpdateView.as_view(),
         name='dashboard-incident-ajax'),
    path('dashboard/incident/<int:pk>/delete/', views.DashboardIncidentDeleteView.as_view(),
         name='dashboard-incident-delete'),

    # Dashboard mediaincident views
    path('dashboard/mediaincident/create/', views.DashboardMediaIncidentCreateView.as_view(),
         name='dashboard-mediaincident-create'),
    path('dashboard/mediaincident/<int:pk>/update/', views.DashboardMediaIncidentUpdateView.as_view(),
         name='dashboard-mediaincident-update'),
    path('dashboard/mediaincident/<int:pk>/ajax/', views.MediaIncidentAjaxUpdateView.as_view(),
         name='dashboard-mediaincident-ajax'),
    path('dashboard/mediaincident/<int:pk>/delete/', views.DashboardMediaIncidentDeleteView.as_view(),
         name='dashboard-mediaincident-delete'),

    path('dashboard/user/update/', views.UserUpdateView.as_view(), name='dashboard-user-update'),
    path('dashboard/user/<int:pk>', views.UserDetailView.as_view(), name='dashboard-user-detail'),

    path('dashboard/campaign/', views.DashboardCampaignCreateView.as_view(), name='dashboard-campaign-create'),
    path('dashboard/campaign/<int:pk>/', views.DashboardCampaignUpdateView.as_view(), name='dashboard-campaign-update'),
    path('dashboard/campaign/<int:pk>/saved/', views.DashboardCampaignUpdatedView.as_view(), name='dashboard-campaign-updated'),
    path('dashboard/campaigns/', views.DashboardCampaignListView.as_view(), name='dashboard-campaign-list'),
    path('dashboard/campaign/<int:pk>/export/', views.DashboardCampaignIncidentsExportView.as_view(), name='dashboard-campaign-incidents-export'),

    path('dashboard/articles/', views.DashboardArticlesView.as_view(), name='dashboard-article-list'),
    path('dashboard/articles/data/', views.ArticleDataView.as_view(), name='dashboard-articles-data'),
    path('dashboard/article/<int:pk>/', views.DashboardArticleApproveView.as_view(), name='dashboard-article-approve'),

    path('dashboard/tags/', views.DashboardTagListView.as_view(),
         name='dashboard-tag-list'),
    path('dashboard/tag/create/', views.DashboardTagCreateView.as_view(),
         name='dashboard-tag-create'),
    path('dashboard/tag/<int:pk>/update/', views.DashboardTagUpdateView.as_view(),
         name='dashboard-tag-update'),
    path('dashboard/tag/<int:pk>/saved/', views.DashboardTagUpdatedView.as_view(),
         name='dashboard-tag-updated'),

    path('dashboard/trash/incidents/', views.DashboardTrashView.as_view(),
         name='dashboard-trash-list'),
    path('dashboard/trash/campaigns/', views.DashboardDeletedCampaignListView.as_view(),
         name='dashboard-trash-campaigns'),
    path('dashboard/trash/posts/', views.DashboardDeletedPostListView.as_view(),
         name='dashboard-trash-posts'),

    path('dashboard/posts/', views.DashboardPostListView.as_view(),
         name='dashboard-posts'),
    path('dashboard/posts/data/', views.DashboardPostDataView.as_view(),
         name='dashboard-posts-data'),
    path('dashboard/post/create/', views.DashboardPostCreateView.as_view(),
         name='dashboard-post-create'),
    path('dashboard/post/<int:pk>/update/', views.DashboardPostUpdateView.as_view(),
         name='dashboard-post-update'),
    path('dashboard/post/<int:pk>/update/saved/', views.DashboardPostUpdatedView.as_view(),
         name='dashboard-post-updated'),

    path("dashboard/updated/",
         views.DashboardStageSuccessView.as_view(),
         name="dashboard-updated"),

    path("dashboard/campaign/<int:campaign_pk>/stage/",
         views.DashboardStageFormCreateView.as_view(),
         name="dashboard-stage-form-empty"),
    path("dashboard/campaign/<int:campaign_pk>/stage/<int:stage_pk>/",
         views.DashboardStageFormUpdateView.as_view(),
         name="dashboard-stage-form-update"),
    path("dashboard/campaign/<int:campaign_pk>/stage/create/",
         views.DashboardStageUpdateView.as_view(),
         name="dashboard-stage-create"),
    path("dashboard/campaign/<int:campaign_pk>/stage/<int:stage_pk>/update/",
         views.DashboardStageUpdateView.as_view(),
         name="dashboard-stage-update"),
    path("dashboard/stage/<int:pk>/delete/",
         views.DashboardStageDeleteView.as_view(),
         name="dashboard-stage-delete"),

    # Dashboard explanation
    path("dashboard/campaign/<int:campaign_pk>/explanation/",
         views.DashboardExplanationFormCreateView.as_view(),
         name="dashboard-explanation-form-empty"),
    path("dashboard/campaign/<int:campaign_pk>/explanation/<int:explanation_pk>/",
         views.DashboardExplanationFormUpdateView.as_view(),
         name="dashboard-explanation-form-update"),
    path("dashboard/campaign/<int:campaign_pk>/explanation/create/",
         views.DashboardExplanationUpdateView.as_view(),
         name="dashboard-explanation-create"),
    path("dashboard/campaign/<int:campaign_pk>/explanation/<int:explanation_pk>/update/",
         views.DashboardExplanationUpdateView.as_view(),
         name="dashboard-explanation-update"),
    path("dashboard/explanation/<int:pk>/delete/",
         views.DashboardExplanationDeleteView.as_view(),
         name="dashboard-explanation-delete"),


    path("dashboard/page/",
         views.DashboardCampaignPageCreateView.as_view(),
         name="dashboard-campaign-page-create"),
    path("dashboard/page/<int:pk>/",
         views.DashboardCampaignPageUpdateView.as_view(),
         name="dashboard-campaign-page-update"),


    path('grabber/algorithms/', views.GrabberAlogrithmsView.as_view(),
         name='grabber-algorithms'),
    path('grabber/algorithms_data/', views.GrabberAlgorithmsDataView.as_view(),
         name='grabber-algorithms-data'),
    path('grabber/source_statistics/',
         views.GrabberSourceStatisticsView.as_view(),
         name='grabber-source-statistics'),

    path('dashboard/campaign/<int:pk>/incidents/',
         views.DashboardCampaignIncidentsListView.as_view(),
         name='dashboard-campaign-incidents'),

    path('dashboard/campaign/<int:pk>/incidents/data/',
         views.DashboardCampaignIncidentsDataView.as_view(),
         name='dashboard-campaign-incidents-data'),
    path('dashboard/userincidents/download/csv', views.download_user_incidents_as_csv, name="download_incidents_csv")

]

app_name = 'core'
