from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from server.apps.core.models import Article, MediaIncident, Source

from ..filters import (
    ARTICLE_ORDERING_FIELDS,
    INCIDENT_ORDERING_FIELDS,
    SOURCE_ORDERING_FIELDS,
)
from ..permissions import IsAdminOrReadOnly
from ..serializers import ArticleSerializer, MediaIncidentSerializer, SourceSerializer


class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.order_by("url")
    serializer_class = SourceSerializer
    permission_classes = [IsAdminOrReadOnly]
    ordering_fields = SOURCE_ORDERING_FIELDS
    action_ordering_fields = {
        "articles_by_url": ARTICLE_ORDERING_FIELDS,
        "media_incidents": INCIDENT_ORDERING_FIELDS,
    }

    def _paginated_response(self, queryset, serializer_class):
        page = self.paginate_queryset(self.filter_queryset(queryset))
        return self.get_paginated_response(serializer_class(page, many=True).data)

    @swagger_auto_schema(
        operation_description="Retrieve articles by source URL with optional filtering and sorting",  # noqa: E501
        manual_parameters=[
            openapi.Parameter(
                "url",
                openapi.IN_QUERY,
                description="URL of the source",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                description="Limit the number of results",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "order_by",
                openapi.IN_QUERY,
                description="Order by field (e.g., 'published_at', 'title')",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: ArticleSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="by_url/articles")
    def articles_by_url(self, request, pk=None):
        url = request.query_params.get("url")
        if not url:
            return Response(
                {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        source = Source.objects.filter(url=url).first()
        if source is None:
            return Response(
                {"error": "Source not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return self._paginated_response(
            Article.objects.filter(source=source).order_by("-create_date"),
            ArticleSerializer,
        )

    @swagger_auto_schema(
        operation_description="Retrieve media incidents by source with optional filtering and sorting",  # noqa: E501
        manual_parameters=[
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                description="Limit the number of results",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "order_by",
                openapi.IN_QUERY,
                description="Order by field (e.g., 'detected_at', 'description')",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: MediaIncidentSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="by_url/media_incidents")
    def media_incidents(self, request):
        url = request.query_params.get("url")
        if not url:
            return Response(
                {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        articles = Article.objects.filter(source__url=url)
        return self._paginated_response(
            MediaIncident.objects.filter(article__in=articles).order_by("-create_date"),
            MediaIncidentSerializer,
        )

    @swagger_auto_schema(
        method="get",
        operation_description="Retrieve a single article by URL",
        manual_parameters=[
            openapi.Parameter(
                "url",
                openapi.IN_QUERY,
                description="URL of the article",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: ArticleSerializer},
    )
    @action(detail=False, methods=["get"], url_path="by_url")
    def by_url(self, request):
        url = request.query_params.get("url")
        if not url:
            return Response(
                {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        source = Source.objects.filter(url=url).first()
        if source is None:
            return Response(
                {"error": "Source not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(self.get_serializer(source).data)

    @swagger_auto_schema(
        method="delete",
        operation_description="Delete source by URL",
        responses={204: "No Content"},
    )
    @action(detail=False, methods=["delete"], url_path="by_url")
    @by_url.mapping.delete
    def delete_by_url(self, request):
        url = request.data.get("url")
        if not url:
            return Response(
                {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        source = Source.objects.filter(url=url).first()
        if source is None:
            return Response(
                {"error": "Source not found"}, status=status.HTTP_404_NOT_FOUND
            )
        source.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        methods=["put", "patch"],
        operation_description="Update source by URL",
        request_body=SourceSerializer,
        responses={200: SourceSerializer},
    )
    @action(detail=False, methods=["put", "patch"], url_path="by_url")
    @by_url.mapping.put
    @by_url.mapping.patch
    def update_by_url(self, request):
        url = request.data.get("url")
        if not url:
            return Response(
                {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        source = Source.objects.filter(url=url).first()
        if source is None:
            return Response(
                {"error": "Source not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(
            source, data=request.data, partial=request.method == "PATCH"
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
