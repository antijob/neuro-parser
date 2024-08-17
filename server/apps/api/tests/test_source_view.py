import pytest

@pytest.mark.django_db
def test_list_sources(api_client, source):
    response = api_client.get("/api/sources/")
    assert response.status_code == 200
    assert response.json()[0]["url"] == source.url


@pytest.mark.django_db
def test_list_sources_with_limit(api_client, source):
    response = api_client.get("/api/sources/", {"limit": 1})
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.django_db
def test_list_sources_invalid_limit(api_client):
    response = api_client.get("/api/sources/", {"limit": "invalid"})
    assert response.status_code == 400


@pytest.mark.django_db
def test_get_articles_by_source_url(api_client, article):
    response = api_client.get(
        "/api/sources/by_url/articles/", {"url": article.source.url}
    )
    assert response.status_code == 200
    assert response.json()[0]["url"] == article.url


@pytest.mark.django_db
def test_get_articles_by_source_url_not_found(api_client):
    response = api_client.get(
        "/api/sources/by_url/articles/", {"url": "http://example.com/unknown-source"}
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_get_media_incidents_by_source_url(api_client, article):
    response = api_client.get(
        "/api/sources/by_url/media_incidents/", {"url": article.source.url}
    )
    assert response.status_code == 200
    assert response.json() == []
