from rest_framework import serializers
from ..core.models import BaseIncident, MediaIncident, IncidentType, Article, Source


class IncidentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentType
        fields = [
            'id', 
            'description', 
            'treshold', 
            'chat_gpt_prompt', 
            'is_active', 
            'should_sent_to_bot',
        ]


# class BaseIncidentSerializer(serializers.ModelSerializer):
#     incident_type = IncidentTypeSerializer()

#     class Meta:
#         model = BaseIncident
#         # fields = '__all__'
#         fields = [
#             'title',
#             'description',
#             'status',
#             'create_date',
#             'update_date',
#             # 'assigned_to', # exclude
#             'region',
#             'incident_type',
#             'count',
#             'urls',
#             'public_title',
#             'public_description'
#         ]

class MediaIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaIncident
        # fields = BaseIncidentSerializer.Meta.fields
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

class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'

class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'
