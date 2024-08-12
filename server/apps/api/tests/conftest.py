import pytest

from rest_framework.test import APIClient
from server.apps.core.models import Source, Article, MediaIncident, IncidentType


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def source():
    return Source.objects.create(url="http://example.com/test-source")


@pytest.fixture
def article(source):
    return Article.objects.create(
        title="Test Article",
        text="This is a test article.",
        url="http://example.com/test-article",
        source=source,
    )
