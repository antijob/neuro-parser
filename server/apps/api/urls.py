from django.urls import path
from .views import GetLastMediaIncidents, GetIncidentTypes, CheckLinkForIncident, CheckTextForIncident

urlpatterns = [
    path('api/incident', GetLastMediaIncidents.as_view(), name='incident'),
    path('api/incident/types', GetIncidentTypes.as_view(), name='incident-types'),
    path('api/check/article', CheckLinkForIncident.as_view(), name='check-article'),
    path('api/check/text', CheckTextForIncident.as_view(), name='check-text'),
]

app_name="api"


'''
GET /api/incident?type=...&days=...
GET /api/incident/types
POST /api/check/text [text = text]
POST /api/check/article [link=link, create_incident=true]
'''