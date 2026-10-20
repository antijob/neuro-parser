import pytest

from server.apps.api.exception_handler import custom_exception_handler
from server.apps.core.models import Article, Source


@pytest.fixture
def many_articles(source):
    Article.objects.bulk_create(
        Article(url=f"http://example.com/a{i}", title=f"t{i:03d}", source=source)
        for i in range(120)
    )


@pytest.mark.django_db
def test_list_has_pagination_envelope(api_client, many_articles):
    data = api_client.get("/api/articles/").json()
    assert set(data) == {"count", "next", "previous", "results"}
    assert data["count"] == 120


@pytest.mark.django_db
def test_default_page_size(api_client, many_articles):
    assert len(api_client.get("/api/articles/").json()["results"]) == 50


@pytest.mark.django_db
def test_limit_is_capped(api_client, many_articles):
    data = api_client.get("/api/articles/", {"limit": 1000}).json()
    assert len(data["results"]) == 100


@pytest.mark.django_db
def test_order_by_allowed_field(api_client, many_articles):
    data = api_client.get("/api/articles/", {"order_by": "-title"}).json()
    assert data["results"][0]["title"] == "t119"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url",
    [
        "/api/articles/",
        "/api/sources/",
        "/api/media-incidents/",
        "/api/sources/by_url/media_incidents/",
        "/api/sources/by_url/articles/",
    ],
)
@pytest.mark.parametrize("field", ["assigned_to__password", "text", "-id"])
def test_order_by_outside_allow_list_rejected(api_client, source, url, field):
    response = api_client.get(url, {"url": source.url, "order_by": field})
    assert response.status_code == 400
    assert "order_by" in response.json()


@pytest.mark.django_db
def test_source_articles_ordering_uses_article_fields(api_client, source):
    response = api_client.get(
        "/api/sources/by_url/articles/",
        {"url": source.url, "order_by": "-publication_date"},
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_sources_reject_article_only_field(api_client):
    response = api_client.get("/api/sources/", {"order_by": "publication_date"})
    assert response.status_code == 400


def test_unhandled_error_is_generic(caplog):
    response = custom_exception_handler(RuntimeError("secret detail"), {})
    assert response.status_code == 500
    assert "secret detail" not in str(response.data)
    assert "secret detail" in caplog.text


@pytest.mark.django_db
def test_article_not_found_is_404(staff_client):
    response = staff_client.delete(
        "/api/articles/by_url/", {"url": "http://example.com/missing"}
    )
    assert response.status_code == 404
    assert Source.objects.count() == 0
