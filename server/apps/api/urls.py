from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IncidentTypeViewSet, MediaIncidentViewSet, SourceViewSet, ArticleViewSet

router = DefaultRouter()
router.register(r'incident-types', IncidentTypeViewSet)
router.register(r'media-incidents', MediaIncidentViewSet)
router.register(r'sources', SourceViewSet)
router.register(r'articles', ArticleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
