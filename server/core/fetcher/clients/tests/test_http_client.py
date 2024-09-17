import pytest
from server.core.fetcher.client import NPClient
from server.core.fetcher.client import NPClient
from server.core.fetcher.libs.exceptions import BadCodeException
from server.apps.core.models import Article, Source
from server.core.article_parser import ArticleParser

import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_get_article_success(load_test_data, mock_aiohttp, article, source):
    logging.debug(load_test_data)
    content = load_test_data("article.html")
    content_article = Article()
    ArticleParser.postprocess_article(content_article, content)
    parsed_text = content_article.text

    mock_aiohttp.get(article.url, status=200, body=content)

    async with NPClient() as client:
        try:
            result = await client.get_article(article, source)
        except Exception as e:
            logging.error(f"Error during get_article call: {e}")
            raise

    logging.debug(f"Result: {result}")
    logging.debug(f"Article after processing: {article}")

    assert result == article
    assert article.redirect_url is None
    assert article.is_redirect is False
    assert article.text == parsed_text


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_get_article_redirect(load_test_data, mock_aiohttp, article, source):
    content = load_test_data("article.html")
    redirect_url = "http://example.com/article-redirect"

    # Мокаем запрос с редиректом
    mock_aiohttp.get(
        article.url,
        status=307,
        body=content,
        headers={"Location": redirect_url},
    )
    mock_aiohttp.get(redirect_url, status=200, body=content)

    async with NPClient() as client:
        result = await client.get_article(article, source)

    assert result != article
    assert article.redirect_url == redirect_url
    assert article.is_redirect is True


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_get_article_bad_code(mock_aiohttp, article, source):
    mock_aiohttp.get(article.url, status=404)

    async with NPClient() as client:
        with pytest.raises(BadCodeException):
            await client.get_article(article, source)


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_get_source_success(load_test_data, mock_aiohttp, source):
    content = load_test_data("source.html")
    mock_aiohttp.get(source.url, status=200, body=content)

    async with NPClient() as client:
        result = await client.get_source(source)

    assert result == content


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_get_source_bad_code(mock_aiohttp, source):
    mock_aiohttp.get(source.url, status=500)

    async with NPClient() as client:
        with pytest.raises(BadCodeException):
            await client.get_source(source)
