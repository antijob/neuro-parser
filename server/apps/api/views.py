from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, schema
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from server.apps.core.models import Source, Article, MediaIncident, IncidentType
from .serializers import (
    MediaIncidentSerializer,
    IncidentTypeSerializer,
    ArticleSerializer,
    SourceSerializer,
)
from server.core.fetcher import Fetcher
from server.core.incident_predictor import IncidentPredictor
from .permissions import IsAdminOrReadOnly, IsAdminOrRestrictedPost


class IncidentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IncidentType.objects.all()
    serializer_class = IncidentTypeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def update(self, request, *args, **kwargs):
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, "_prefetched_objects_cache", None):
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class MediaIncidentViewSet(viewsets.ModelViewSet):
    queryset = MediaIncident.objects.all()
    serializer_class = MediaIncidentSerializer
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(
        operation_description="Retrieve incidents by article",
        responses={200: MediaIncidentSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def by_article(self, request, pk=None):
        try:
            incidents = self.queryset.filter(article_id=pk)
            serializer = self.get_serializer(incidents, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    permission_classes = [IsAdminOrReadOnly]

    @swagger_auto_schema(
        operation_description="Retrieve sources with optional filtering and sorting",
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
                description="Order by field (e.g., 'name', 'created_at')",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: SourceSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            sources = Source.objects.all()

            # Apply ordering
            try:
                order_by = request.query_params.get("order_by", None)
                if order_by:
                    sources = sources.order_by(order_by)
            except Exception as e:
                return Response(
                    {"error": f"Invalid order_by value: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Apply limit
            try:
                limit = request.query_params.get("limit", None)
                if limit:
                    limit = int(limit)
                    sources = sources[:limit]
            except ValueError:
                return Response(
                    {"error": "Invalid limit value"}, status=status.HTTP_400_BAD_REQUEST
                )

            serializer = SourceSerializer(sources, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Retrieve sources with optional filtering and sorting",
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
                description="Order by field (e.g., 'published_at', 'title')",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: ArticleSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def articles(self, request, pk=None):
        try:
            source = self.get_object()
            articles = Article.objects.filter(source=source)

            # Apply ordering
            try:
                order_by = request.query_params.get("order_by", None)
                if order_by:
                    articles = articles.order_by(order_by)
            except Exception as e:
                return Response(
                    {"error": f"Invalid order_by value: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Apply limit
            try:
                limit = request.query_params.get("limit", None)
                if limit:
                    limit = int(limit)
                    articles = articles[:limit]
            except ValueError:
                return Response(
                    {"error": "Invalid limit value"}, status=status.HTTP_400_BAD_REQUEST
                )

            serializer = ArticleSerializer(articles, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Retrieve media incidents by source with optional filtering and sorting",
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
    @action(detail=True, methods=["get"])
    def media_incidents(self, request, pk=None):
        try:
            source = self.get_object()
            articles = Article.objects.filter(source=source)
            incidents = MediaIncident.objects.filter(article__in=articles)

            # Apply ordering
            try:
                order_by = request.query_params.get("order_by", None)
                if order_by:
                    incidents = incidents.order_by(order_by)
            except Exception as e:
                return Response(
                    {"error": f"Invalid order_by value: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Apply limit
            try:
                limit = request.query_params.get("limit", None)
                if limit:
                    limit = int(limit)
                    incidents = incidents[:limit]
            except ValueError:
                return Response(
                    {"error": "Invalid limit value"}, status=status.HTTP_400_BAD_REQUEST
                )

            serializer = MediaIncidentSerializer(incidents, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminOrRestrictedPost]

    @swagger_auto_schema(
        operation_description="Retrieve articles with optional filtering and sorting",
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
                description="Order by field (e.g., 'published_at', 'title')",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: ArticleSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            articles = Article.objects.all()

            # Apply ordering
            try:
                order_by = request.query_params.get("order_by", None)
                if order_by:
                    articles = articles.order_by(order_by)
            except Exception as e:
                return Response(
                    {"error": f"Invalid order_by value: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Apply limit
            try:
                limit = request.query_params.get("limit", None)
                if limit:
                    limit = int(limit)
                    articles = articles[:limit]
            except ValueError:
                return Response(
                    {"error": "Invalid limit value"}, status=status.HTTP_400_BAD_REQUEST
                )

            serializer = ArticleSerializer(articles, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Retrieve media incidents by source with optional filtering and sorting",
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
    @action(detail=True, methods=["get"])
    def media_incidents(self, request, pk=None):
        try:
            source = self.get_object()
            articles = Article.objects.filter(source=source)
            incidents = MediaIncident.objects.filter(article__in=articles)

            # Apply ordering
            try:
                order_by = request.query_params.get("order_by", None)
                if order_by:
                    incidents = incidents.order_by(order_by)
            except Exception as e:
                return Response(
                    {"error": f"Invalid order_by value: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Apply limit
            try:
                limit = request.query_params.get("limit", None)
                if limit:
                    limit = int(limit)
                    incidents = incidents[:limit]
            except ValueError:
                return Response(
                    {"error": "Invalid limit value"}, status=status.HTTP_400_BAD_REQUEST
                )

            serializer = MediaIncidentSerializer(incidents, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminOrRestrictedPost]

    @swagger_auto_schema(
        operation_description="Retrieve articles with optional filtering and sorting",
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
                description="Order by field (e.g., 'published_at', 'title')",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: ArticleSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        try:
            articles = Article.objects.all()

            # Apply ordering
            try:
                order_by = request.query_params.get("order_by", None)
                if order_by:
                    articles = articles.order_by(order_by)
            except Exception as e:
                return Response(
                    {"error": f"Invalid order_by value: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Apply limit
            try:
                limit = request.query_params.get("limit", None)
                if limit:
                    limit = int(limit)
                    articles = articles[:limit]
            except ValueError:
                return Response(
                    {"error": "Invalid limit value"}, status=status.HTTP_400_BAD_REQUEST
                )

            serializer = ArticleSerializer(articles, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Retrieve articles by URL",
        responses={200: ArticleSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def by_url(self, request, pk=None):
        try:
            articles = self.queryset.filter(url=pk)
            serializer = self.get_serializer(articles, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Fetch article from URL",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "url": openapi.Schema(
                    type=openapi.TYPE_STRING, description="URL of the article"
                ),
            },
        ),
        responses={200: ArticleSerializer},
    )
    @action(detail=False, methods=["post"])
    def fetch(self, request):
        try:
            url = request.data.get("url")
            if not url:
                return Response(
                    {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Create an Article object
            article = Article.objects.create(url=url)

            # Call external methods
            Fetcher.fetch_article(article)

            # Serialize and return the Article object
            article_serializer = self.get_serializer(article)
            return Response({"article": article_serializer.data})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Predict incidents for an article",
        responses={200: MediaIncidentSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def predict(self, request, pk=None):
        try:
            article = self.get_object()
            if not article.is_downloaded:
                return Response(
                    {"error": "Article not fetched"}, status=status.HTTP_400_BAD_REQUEST
                )

            predictor = IncidentPredictor()
            incidents = predictor.predict(article)

            # Serialize and return the created MediaIncident
            incidents_serializer = MediaIncidentSerializer(incidents, many=True)
            return Response({"incidents": incidents_serializer.data})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
