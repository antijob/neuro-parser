import datetime
import pytest
from unittest.mock import patch, MagicMock

from server.apps.core.models import Article

from server.core.article_parser.article_parser import ArticleParser
from server.core.article_parser.parsers.vk_parser import VkParser
from server.core.article_parser.parsers.ok_parser import OkParser
from server.core.article_parser.parsers.tg_parser import TgParser
from server.core.article_parser.parsers.common_parser import CommonParser


@pytest.mark.parametrize(
    "url,expected_parser",
    [
        ("https://vk.com/some_post", VkParser),
        ("https://ok.ru/some_post", OkParser),
        ("https://t.me/some_channel", TgParser),
        ("https://example.com/some_article", CommonParser),
    ],
)
def test_registry_choose(url, expected_parser):
    assert ArticleParser.registry.choose(url) == expected_parser


@pytest.mark.parametrize(
    "html_content,expected_title,expected_text,expected_date",
    [
        (
            """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Sample Title</title>
            </head>
            <body>
                <div class="article">
                    <h1>Sample Title</h1>
                    <div class="content">
                        <p>This is the main content of the article.</p>
                    </div>
                    <div class="date">
                        <p>Publication Date: 2024-09-01</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "Sample Title",
            "This is the main content of the article.",
            "2024-09-01",
        ),
        (
            """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Another Title</title>
            </head>
            <body>
                <div class="article">
                    <h1>Another Title</h1>
                    <div class="content">
                        <p>Another content of the article.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "Another Title",
            "Another content of the article.",
            None,  # This will default to today's date if not provided
        ),
    ],
)
def test_postprocess_article_with_html(
    html_content, expected_title, expected_text, expected_date
):
    # Create an Article instance with a URL that would be handled by CommonParser
    article = Article(url="https://example.com/some_article")

    if not expected_date:
        expected_date = datetime.date.today()

    ArticleParser.postprocess_article(article, html_content)

    # Check if the article's fields have been updated correctly
    assert article.title == expected_title
    assert article.text == expected_text

    # ToDo: add test for date
