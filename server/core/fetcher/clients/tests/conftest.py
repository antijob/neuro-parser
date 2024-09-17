from itertools import count
import pytest
from server.apps.core.models import Article, Source, Country
from pathlib import Path
from aioresponses import aioresponses


# Фикстура для загрузки данных из файла
@pytest.fixture
def load_test_data():
    def _load(filename):
        filepath = Path(__file__).parent / "test_data" / filename
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()

    return _load


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
