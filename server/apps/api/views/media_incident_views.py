from rest_framework import viewsets



from server.apps.core.models import MediaIncident


from ..serializers import MediaIncidentSerializer
from ..permissions import IsAdminOrReadOnly


class MediaIncidentViewSet(viewsets.ModelViewSet):
    queryset = MediaIncident.objects.all()
    serializer_class = MediaIncidentSerializer
    permission_classes = [IsAdminOrReadOnly]
