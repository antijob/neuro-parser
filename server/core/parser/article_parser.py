from typing import Any, List
from .parsers.base_parser import ArticleData, ParserBase

from .parsers.tg_parser import TgParser
from .parsers.vk_parser import VkParser
from .parsers.ok_parser import OkParser
from .parsers.common_parser import CommonParser

from server.apps.core.models import Article

import datetime


# ToDo: ArticleData не должна быть завязана на url'е  -- это информация о контенте
# Единственная причина, почему final_url остается в ArticleData -- он может переопределиться в CommonParser.get_page_data
class ArticleParser:
    parsers: List[ParserBase] = [VkParser, OkParser, TgParser, CommonParser]

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
    def postprocess_article(cls, article: Article, data: Any) -> None:
        article_data: ArticleData = cls.parse_article_raw_data(article.url, data)
        if article_data:
            article.title, article.text, publication_date, article.url = article_data
            if publication_date:
                article.publication_date = publication_date
            else:
                article.publication_date = datetime.date.today()
        article.is_downloaded = True
        # article.save()
