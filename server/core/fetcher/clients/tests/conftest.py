from itertools import count
import pytest
from server.apps.core.models import Article, Source, Country
from aioresponses import aioresponses

from server.libs.helpers import load_pytest_data


@pytest.fixture
def load_test_data():
    return load_pytest_data(__file__)


@pytest.fixture
def mock_aiohttp():
    with aioresponses() as mocker:
        yield mocker


# Фикстура для создания объекта Source
@pytest.fixture
def source():
    country = Country.objects.create(name="tetst")
    return Source.objects.create(url="http://example.com", country=country)


# Фикстура для создания объекта Article
@pytest.fixture
def article(source):
    return Article.objects.create(url="http://example.com/article", source=source)
