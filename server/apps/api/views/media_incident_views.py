from rest_framework import viewsets


from server.apps.core.models import MediaIncident


from ..filters import INCIDENT_ORDERING_FIELDS
from ..serializers import MediaIncidentSerializer
from ..permissions import IsAdminOrReadOnly


class MediaIncidentViewSet(viewsets.ModelViewSet):
    queryset = MediaIncident.objects.order_by("-create_date")
    serializer_class = MediaIncidentSerializer
    permission_classes = [IsAdminOrReadOnly]
    ordering_fields = INCIDENT_ORDERING_FIELDS
