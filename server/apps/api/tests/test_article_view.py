import pytest
from server.apps.core.models import Article


@pytest.mark.django_db
def test_get_article_by_url(api_client, article):
    response = api_client.get("/api/articles/by_url/", {"url": article.url})
    assert response.status_code == 200
    assert response.json()["url"] == article.url


@pytest.mark.django_db
def test_update_article_by_url(api_client, article):
    new_title = "Updated Test Article"
    response = api_client.patch(
        "/api/articles/by_url/", {"url": article.url, "title": new_title}
    )

    assert response.status_code == 200
    article.refresh_from_db()
    assert article.title == new_title


@pytest.mark.django_db
def test_get_article_by_url_not_found(api_client):
    response = api_client.get(
        "/api/articles/by_url/", {"url": "http://example.com/unknown-article"}
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_article_by_url(api_client, article):
    assert article.url == "http://example.com/test-article"
    response = api_client.delete(
        "/api/articles/by_url/", {"url": "http://example.com/test-article"}
    )

    assert response.status_code == 204
    assert not Article.objects.filter(url=article.url).exists()
    assert response.content == b""


# @pytest.mark.django_db
# def test_fetch_article(api_client, article, mocker):
#     fetcher_mock = mocker.patch(
#         "server.core.fetcher.Fetcher.download_article", return_value=None
#     )
#     response = api_client.get("/api/articles/by_url/fetch/", {"url": article.url})
#     assert response.status_code == 200
#     fetcher_mock.assert_called_once_with(article)


# @pytest.mark.django_db
# def test_predict_incidents(api_client, article, mocker):
#     mock_incidents = [MediaIncident(description="Test incident")]
#     predictor_mock = mocker.patch(
#         "server.core.incident_predictor.IncidentPredictor.predict",
#         return_value=mock_incidents,
#     )
#     response = api_client.get("/api/articles/by_url/predict/", {"url": article.url})
#     assert response.status_code == 200
#     predictor_mock.assert_called_once_with(article)
