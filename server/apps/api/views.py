import logging
from asgiref.sync import async_to_sync


from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from server.apps.core.models import Source, Article, MediaIncident, IncidentType
from server.core.fetcher import Fetcher
from server.core.incident_predictor import IncidentPredictor


from .serializers import (
    MediaIncidentSerializer,
    IncidentTypeSerializer,
    ArticleSerializer,
    SourceSerializer,
)
from .permissions import IsAdminOrReadOnly, IsAdminOrRestrictedPost


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


class MediaIncidentViewSet(viewsets.ModelViewSet):
    queryset = MediaIncident.objects.all()
    serializer_class = MediaIncidentSerializer
    permission_classes = [IsAdminOrReadOnly]


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
        operation_description="Retrieve articles by source URL with optional filtering and sorting",
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
        try:
            url = request.query_params.get("url")
            if not url:
                return Response(
                    {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            source = Source.objects.get(url=url)
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
    @action(detail=False, methods=["get"], url_path="by_url/media_incidents")
    def media_incidents(self, request):
        try:
            url = request.query_params.get("url")
            if not url:
                return Response(
                    {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            articles = Article.objects.filter(source__url=url)
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
        try:
            url = request.query_params.get("url")
            if not url:
                return Response(
                    {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            source = self.queryset.get(url=url)
            serializer = self.get_serializer(source)
            return Response(serializer.data)
        except Source.DoesNotExist:
            return Response(
                {"error": "Source not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method="delete",
        operation_description="Delete source by URL",
        responses={204: "No Content"},
    )
    @action(detail=False, methods=["delete"], url_path="by_url")
    @by_url.mapping.delete
    def delete_by_url(self, request):
        try:
            url = request.query_params.get("url")
            if not url:
                return Response(
                    {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            source = Source.objects.get(url=url)
            source.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        methods=["put", "patch"],
        operation_description="Update source by URL",
        request_body=SourceSerializer,
        responses={200: SourceSerializer},
    )
    @action(detail=False, methods=["put", "patch"], url_path="by_url")
    @by_url.mapping.put  #
    @by_url.mapping.patch
    def update_by_url(self, request):
        try:
            url = request.query_params.get("url")
            if not url:
                return Response(
                    {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            partial = request.method == "PATCH"
            source = Source.objects.get(url=url)
            serializer = self.get_serializer(source, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(source, "_prefetched_objects_cache", None):
                source._prefetched_objects_cache = {}

            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # @swagger_auto_schema(
    #     operation_description="Retrieve source by URL",
    #     manual_parameters=[
    #         openapi.Parameter('url', openapi.IN_QUERY, description="URL of the source", type=openapi.TYPE_STRING),
    #     ],
    #     responses={200: SourceSerializer}
    # )
    # @by_url.mapping.get
    # @action(detail=False, methods=['get'], url_path='by_url')
    # def get_by_url(self, request):
    #     try:
    #         url = request.query_params.get('url')
    #         if not url:
    #             return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)

    #         source = Source.objects.get(url=url)
    #         serializer = self.get_serializer(source)
    #         return Response(serializer.data)
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
                description="Order by field (e.g., 'name', 'created_at')",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: SourceSerializer(many=True)},
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
        try:
            url = request.query_params.get("url")
            if not url:
                return Response(
                    {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            article = self.queryset.get(url=url)
            serializer = self.get_serializer(article)
            return Response(serializer.data)
        except Article.DoesNotExist:
            return Response(
                {"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method="delete",
        operation_description="Delete article by URL",
        responses={204: "No Content"},
    )
    @by_url.mapping.delete
    @action(detail=False, methods=["delete"], url_path="by_url")
    def delete_by_url(self, request):
        try:
            url = request.query_params.get("url")
            if not url:
                return Response(
                    {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            article = Article.objects.get(url=url)
            article.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        methods=["put", "patch"],
        operation_description="Update article by URL",
        request_body=ArticleSerializer,
        responses={200: ArticleSerializer},
    )
    @by_url.mapping.put
    @by_url.mapping.patch
    @action(detail=False, methods=["put", "patch"], url_path="by_url")
    def update_by_url(self, request):
        try:
            url = request.query_params.get("url")
            if not url:
                return Response(
                    {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            partial = request.method == "PATCH"
            article = Article.objects.get(url=url)
            serializer = self.get_serializer(
                article, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(article, "_prefetched_objects_cache", None):
                article._prefetched_objects_cache = {}

            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Fetch article from URL",
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
    @action(detail=False, methods=["get"], url_path="by_url/fetch")
    def fetch(self, request):
        try:
            url = request.query_params.get("url")
            if not url:
                return Response(
                    {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            article, created = Article.objects.get_or_create(url=url)

            if created or not article.is_downloaded:
                async_to_sync(Fetcher.download_article)(article)

            article_serializer = self.get_serializer(article)
            return Response({"article": article_serializer.data})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Predict incidents for an article",
        manual_parameters=[
            openapi.Parameter(
                "url",
                openapi.IN_QUERY,
                description="URL of the article",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={200: MediaIncidentSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="by_url/predict")
    def predict(self, request):
        try:
            url = request.query_params.get("url")
            if not url:
                return Response(
                    {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            article = self.queryset.get(url=url)
            if not article.is_downloaded:
                return Response(
                    {"error": "Article not fetched"}, status=status.HTTP_400_BAD_REQUEST
                )

            predictor = IncidentPredictor()
            incidents = predictor.predict(article)

            incidents_serializer = MediaIncidentSerializer(incidents, many=True)
            return Response({"incidents": incidents_serializer.data})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
