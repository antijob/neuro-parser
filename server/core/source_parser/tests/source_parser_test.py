import datetime
import pytest
from unittest.mock import patch, MagicMock

from server.apps.core.models import Source

from server.core.source_parser.source_parser import SourceParser
from server.core.source_parser.parsers.vk_parser import VkParser
from server.core.source_parser.parsers.ok_parser import OkParser
from server.core.source_parser.parsers.tg_parser import TgParser
from server.core.source_parser.parsers.rss_parser import RssParser
from server.core.source_parser.parsers.common_parser import CommonParser


@pytest.mark.parametrize(
    "source_url, expected_parser",
    [
        ("https://vk.com/some_text", VkParser),
        ("https://ok.ru/some_text", OkParser),
        ("https://t.me/some_text", TgParser),
        ("https://example.com/some_text.rss", RssParser),
        ("https://example.com/some_text", CommonParser),
    ],
)
def test_registry_choose(source_url, expected_parser):
    source = Source(url=source_url)
    assert SourceParser.registry.choose(source) == expected_parser
