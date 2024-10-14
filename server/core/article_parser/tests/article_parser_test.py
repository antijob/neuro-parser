import datetime
import pytest
from unittest.mock import patch, MagicMock

from server.apps.core.models import Article

from server.core.article_parser.article_parser import ArticleParser
from server.core.article_parser.parsers.vk_parser import VkParser
from server.core.article_parser.parsers.ok_parser import OkParser
from server.core.article_parser.parsers.tg_parser import TgParser
from server.core.article_parser.parsers.common_parser import CommonParser


from server.libs.helpers import load_pytest_data


@pytest.fixture
def load_test_data():
    return load_pytest_data(__file__)


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
    "html_file,expected_title,expected_text,expected_date",
    [
        (
            "article1.html",
            "Sample Title",
            "This is the main content of the article.",
            "2024-09-01",
        ),
        (
            "article2.html",
            "Another Title",
            "Another content of the article.",
            None,  # This will default to today's date if not provided
        ),
    ],
)
def test_postprocess_article_with_html(
    html_file, expected_title, expected_text, expected_date, load_test_data
):
    # Create an Article instance with a URL that would be handled by CommonParser
    article = Article(url="https://example.com/some_article")

    if not expected_date:
        expected_date = datetime.date.today()

    html_data = load_test_data(html_file)

    ArticleParser.postprocess_article(article, html_data)

    # Check if the article's fields have been updated correctly
    assert article.title == expected_title
    assert article.text == expected_text

    # ToDo: add test for date
