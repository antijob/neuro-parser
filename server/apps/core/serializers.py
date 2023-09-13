from rest_framework import serializers
from .models import BaseIncident, MediaIncident, UserIncident, IncidentType


class IncidentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentType
        fields = ['id', 'description']


class BaseIncidentSerializer(serializers.ModelSerializer):
    incident_type = IncidentTypeSerializer()

    class Meta:
        model = BaseIncident
        fields = '__all__'
        fields = [
            'title',
            'description',
            'status',
            'create_date',
            'update_date',
            # 'assigned_to', # exclude
            'region',
            'incident_type',
            'count',
            'urls',
            'public_title',
            'public_description'
        ]

class MediaIncidentSerializer(BaseIncidentSerializer):
    class Meta:
        model = MediaIncident
        fields = BaseIncidentSerializer.Meta.fields

class UserIncidentSerializer(BaseIncidentSerializer):
    class Meta:
        model = UserIncident
        fields = BaseIncidentSerializer.Meta.fields

