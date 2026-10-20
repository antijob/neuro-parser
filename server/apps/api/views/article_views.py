from asgiref.sync import async_to_sync

from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from server.apps.core.models import Article
from server.core.fetcher import Fetcher
from server.core.incident_predictor import IncidentPredictor


from ..filters import ARTICLE_ORDERING_FIELDS
from ..permissions import IsAdminOrReadOnly
from ..validators import UnsafeURLError, validate_public_http_url
from ..serializers import (
    MediaIncidentSerializer,
    ArticleSerializer,
)


URL_BODY = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=["url"],
    properties={"url": openapi.Schema(type=openapi.TYPE_STRING)},
)


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.order_by("-create_date")
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminOrReadOnly]
    ordering_fields = ARTICLE_ORDERING_FIELDS

    def _get_article(self, url):
        return Article.objects.filter(url=url).first()

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
        url = request.query_params.get("url")
        if not url:
            return Response(
                {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        article = self._get_article(url)
        if article is None:
            return Response(
                {"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(self.get_serializer(article).data)

    @swagger_auto_schema(
        method="delete",
        operation_description="Delete article by URL",
        manual_parameters=[
            openapi.Parameter(
                "url",
                openapi.IN_QUERY,
                description="URL of the article",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={204: "No Content"},
    )
    @by_url.mapping.delete
    @action(detail=False, methods=["delete"], url_path="by_url")
    def delete_by_url(self, request):
        url = request.data.get("url")
        if not url:
            return Response(
                {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        article = self._get_article(url)
        if article is None:
            return Response(
                {"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND
            )
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        url = request.data.get("url")
        if not url:
            return Response(
                {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        article = self._get_article(url)
        if article is None:
            return Response(
                {"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(
            article, data=request.data, partial=request.method == "PATCH"
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Fetch article from URL",
        request_body=URL_BODY,
        responses={200: ArticleSerializer},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="by_url/fetch",
        permission_classes=[IsAdminUser],
    )
    def fetch(self, request):
        url = request.data.get("url")
        if not url:
            return Response(
                {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            validate_public_http_url(url)
        except UnsafeURLError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        article, created = Article.objects.get_or_create(url=url)

        if created or not article.is_downloaded:
            async_to_sync(Fetcher.download_article)(article)

        return Response({"article": self.get_serializer(article).data})

    @swagger_auto_schema(
        operation_description="Predict incidents for an article",
        request_body=URL_BODY,
        responses={200: MediaIncidentSerializer(many=True)},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="by_url/predict",
        permission_classes=[IsAdminUser],
    )
    def predict(self, request):
        url = request.data.get("url")
        if not url:
            return Response(
                {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        article = self._get_article(url)
        if article is None:
            return Response(
                {"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if not article.is_downloaded:
            return Response(
                {"error": "Article not fetched"}, status=status.HTTP_400_BAD_REQUEST
            )

        incidents = IncidentPredictor.predict(article)
        return Response(
            {"incidents": MediaIncidentSerializer(incidents, many=True).data}
        )
