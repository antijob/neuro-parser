from .parsers.tg_parser import TgParser
from .parsers.vk_parser import VkParser
from .parsers.ok_parser import OkParser
from .parsers.common_parser import CommonParser
from .parsers.base_parser import ArticleData


class ArticleParser:
    parsers = [VkParser, OkParser, TgParser, CommonParser]

    @classmethod
    def get_article(cls, url: str) -> ArticleData:
        for parser in cls.parsers:
            if parser.can_handle(url):
                return parser.get_page_data(url)
        raise ValueError("No suitable parser found")

    @classmethod
    def parse_article_raw_data(cls, url: str, data) -> ArticleData:
        for parser in cls.parsers:
            if parser.can_handle(url):
                return parser.parse_raw_data(url, data)
        raise ValueError("No suitable parser found")
