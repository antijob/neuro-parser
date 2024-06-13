from typing import List
from .parsers.base_parser import ArticleData, ParserBase

from .parsers.tg_parser import TgParser
from .parsers.vk_parser import VkParser
from .parsers.ok_parser import OkParser
from .parsers.common_parser import CommonParser

import datetime


# ToDo: ArticleData не должна быть завязана на url'е  -- это информация о контенте
# Единственная причина, почему final_url остается в ArticleData -- он может переопределиться в CommonParser.get_page_data
class ArticleParser:
    parsers: List[ParserBase] = [VkParser, OkParser, TgParser, CommonParser]

    # Это задача не парсера, это задача фетчера
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
                # вот тут не должен прокидываться url
                return parser.parse_raw_data(url, data)
        raise ValueError("No suitable parser found")

    # Этот метод перенесен из модели, пожтому пока что он может делать странные вещи
    # Например, писать, что статья скачана
    @classmethod
    def postprocess_raw_data(self, article, data: ArticleData) -> None:
        if data:
            article.title, article.text, publication_date, article.url = data
            if publication_date:
                article.publication_date = publication_date
            else:
                article.publication_date = datetime.date.today()
        article.is_downloaded = True
        article.save()
