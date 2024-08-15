import pytest

from rest_framework.test import APIClient
from server.apps.core.models import Source, Article, MediaIncident, IncidentType

from server.apps.users.models import User


@pytest.fixture
def staff_user():
    return User(email="staff@example.com", password="testpass", is_staff=True)


@pytest.fixture
def regular_user():
    return User(email="user@example.com", password="testpass")


@pytest.fixture
def api_client(regular_user):
    api_client = APIClient()
    api_client.force_authenticate(user=regular_user)
    return api_client


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
