from goose3 import Goose
from goose3.configuration import Configuration
from urllib.parse import urlparse


from .base_parser import ArticleData, ParserBase
from ..utils import convert_date_format


class CommonParser(ParserBase):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return True  # Default parser

    @classmethod
    def parse_raw_data(cls, data) -> ArticleData:
        config = Configuration()
        config.strict = False

        with Goose(config) as g:
            article = g.extract(raw_html=data)
            title = article.title
            text = article.cleaned_text
            date = convert_date_format(article.publish_date)

        return ArticleData(title, text, date)
