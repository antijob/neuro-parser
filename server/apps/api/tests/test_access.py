import pytest

from server.apps.core.models import Article, Source

READ_URLS = [
    "/api/incident-types/",
    "/api/media-incidents/",
    "/api/sources/",
    "/api/articles/",
]


@pytest.mark.django_db
@pytest.mark.parametrize("url", READ_URLS)
def test_anonymous_cannot_read(anon_client, url):
    response = anon_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_swagger_stays_public(anon_client):
    response = anon_client.get("/swagger-ui/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_regular_user_cannot_delete_article(api_client, article):
    response = api_client.delete("/api/articles/by_url/", {"url": article.url})
    assert response.status_code == 403
    assert Article.objects.filter(url=article.url).exists()


@pytest.mark.django_db
def test_regular_user_cannot_update_source(api_client, source):
    response = api_client.patch(
        "/api/sources/by_url/", {"url": source.url, "is_active": False}
    )
    assert response.status_code == 403
    source.refresh_from_db()
    assert source.is_active is True


@pytest.mark.django_db
def test_staff_can_update_source(staff_client, source):
    response = staff_client.patch(
        "/api/sources/by_url/", {"url": source.url, "is_active": False}
    )
    assert response.status_code == 200
    assert Source.objects.get(url=source.url).is_active is False


@pytest.mark.django_db
@pytest.mark.parametrize("action", ["predict", "fetch"])
def test_side_effect_actions_reject_get(staff_client, article, action):
    response = staff_client.get(f"/api/articles/by_url/{action}/", {"url": article.url})
    assert response.status_code == 405


@pytest.mark.django_db
@pytest.mark.parametrize("action", ["predict", "fetch"])
def test_side_effect_actions_reject_non_staff(api_client, article, action):
    response = api_client.post(f"/api/articles/by_url/{action}/", {"url": article.url})
    assert response.status_code == 403


@pytest.mark.django_db
def test_staff_predict_runs_prediction(staff_client, article, monkeypatch):
    article.is_downloaded = True
    article.save()
    calls = []
    monkeypatch.setattr(
        "server.apps.api.views.article_views.IncidentPredictor.predict",
        lambda a: calls.append(a) or [],
    )
    response = staff_client.post("/api/articles/by_url/predict/", {"url": article.url})
    assert response.status_code == 200
    assert calls == [article]
