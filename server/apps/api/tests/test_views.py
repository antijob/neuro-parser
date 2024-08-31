import pytest


@pytest.mark.django_db
def test_get_sources(api_client):
    # Формируем URL запроса с параметром `url`

    response_get = api_client.get("/api/sources/")

    # Проверяем, что ответ имеет статус 200 OK
    assert response_get.status_code == 200

    # Проверяем, что данные, возвращаемые API, совпадают с данными в базе
    assert response_get.json() == []


@pytest.mark.django_db
def test_get_article_by_url(api_client, article):
    # Формируем URL запроса с параметром `url`

    response_post = api_client.post(
        "/api/articles/",
        {
            "url": "http://example.com/test-article3",
            "title": article.title,
            "text": article.text,
        },
    )

    assert response_post.status_code == 201

    response_get = api_client.get("/api/articles/by_url/", {"url": article.url})
    assert response_get.status_code == 200

    # Проверяем, что данные, возвращаемые API, совпадают с данными в базе
    assert response_get.data["title"] == article.title
    assert response_get.data["text"] == article.text


@pytest.mark.django_db
def test_get_article_by_url_not_found(api_client):
    response = api_client.get(
        "/api/articles/by_url/", {"url": "http://example.com/non-existent-article"}
    )

    assert response.status_code == 404
