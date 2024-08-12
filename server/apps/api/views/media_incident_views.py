import logging

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from server.apps.core.models import Source, Article, MediaIncident, IncidentType


from ..serializers import MediaIncidentSerializer
from ..permissions import IsAdminOrReadOnly, IsAdminOrRestrictedPost
from rest_framework.permissions import AllowAny


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MediaIncidentViewSet(viewsets.ModelViewSet):
    queryset = MediaIncident.objects.all()
    serializer_class = MediaIncidentSerializer
    permission_classes = [AllowAny]
