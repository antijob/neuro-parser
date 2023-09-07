from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, GenericAPIView

from server.apps.core.models import (
    Article,
    MediaIncident, 
    IncidentType,
    UserIncident,
)
from server.apps.core.serializers import MediaIncidentSerializer, IncidentTypeSerializer

from django.utils import timezone
from django.conf import settings
from django.db.models import Q


from server.apps.core.logic.grabber.classificator.category import predict_incident_type


class GetLastMediaIncidents(generics.ListAPIView):
    throttle_scope = 'user' 
    serializer_class = MediaIncidentSerializer

    def get_queryset(self):
        days_count = int(self.request.query_params.get('days', 0)) 
        incident_type = int(self.request.query_params.get('type', -1)) 

        if days_count == 0:
            days_condition = Q() 
        else:
            start_date = timezone.now() - timezone.timedelta(days=days_count)
            days_condition = Q(create_date__gte=start_date)

        if  incident_type == -1:
            incident_condition = Q() 
        else:
            incident_condition = Q(incident_type_id=incident_type)

        queryset = MediaIncident.objects.filter(
            days_condition & incident_condition
        ).order_by('-create_date')

        return queryset


class GetIncidentTypes(generics.ListAPIView):
    throttle_scope = 'user' 
    serializer_class = IncidentTypeSerializer

    def get_queryset(self):
        return IncidentType.objects.all()


class CheckLinkForIncident(CreateAPIView):
    throttle_scope = 'user' 
    serializer_class = MediaIncidentSerializer

    def create(self, request, *args, **kwargs):
        link = request.data.get('link', '')
        create_incident = bool(request.data.get('create_incident', True))

        try:
            article = None
            if link:
                article = Article.objects.create(url=link) # get_or)create if url field will be prime field 
                article.download()
                incident = article.create_incident()
            else:
                incident = None
            
            data = None
            if incident:
                data = MediaIncidentSerializer(incident).data
            if not incident or not create_incident:
                if article:
                    article.delete()
                if incident:
                    incident.delete()

            return Response({'incident': data}, status=status.HTTP_200_OK)#incident
        except Exception as e:
            return Response({'incident': None, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CheckTextForIncident(GenericAPIView):
    throttle_scope = 'user' 
    serializer_class = IncidentTypeSerializer

    def post(self, request, format=None):
        text = request.data.get('text', '')

        if text:
            incident_type = predict_incident_type(text)
            data = {'incident_type': incident_type}
        else:
            incident_type = None

        serializer = self.get_serializer({'incident_type': incident_type})
        return Response(serializer.data, status=status.HTTP_200_OK) #serializer.data
