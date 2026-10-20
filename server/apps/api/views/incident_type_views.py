from rest_framework import viewsets
from rest_framework.response import Response


from server.apps.core.models import IncidentType


from ..serializers import IncidentTypeSerializer
from ..permissions import IsAdminOrReadOnly


class IncidentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IncidentType.objects.order_by("id")
    serializer_class = IncidentTypeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
