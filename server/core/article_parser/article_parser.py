import logging
from typing import Any
import datetime

from .parsers.base_parser import ArticleData, ParserBase
from .parsers.tg_parser import TgParser
from .parsers.vk_parser import VkParser
from .parsers.ok_parser import OkParser
from .parsers.common_parser import CommonParser
from server.apps.core.models import Article
from server.libs.handler import HandlerRegistry


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArticleParser:
    registry = HandlerRegistry[ParserBase]()
    registry.register(VkParser)
    registry.register(OkParser)
    registry.register(TgParser)
    registry.register(CommonParser)

    @classmethod
    def _parse_article_raw_data(cls, url: str, data) -> ArticleData:
        try:
            parser = cls.registry.choose(url)
            return parser.parse_raw_data(data)
        except Exception as e:
            logger.error(f"Error parsing article raw data from URL {url}: {e}")
            raise

    # you should save it by yourself
    @classmethod
    def postprocess_article(cls, article: Article, data: Any) -> None:
        try:
            article_data: ArticleData = cls._parse_article_raw_data(article.url, data)
            if article_data:
                article.title, article.text, publication_date = article_data
                if publication_date:
                    article.publication_date = publication_date
                else:
                    article.publication_date = datetime.date.today()
        except ValueError as e:
            logger.warning(f"Value error during postprocessing of article {article.url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during postprocessing of article {article.url}: {e}")

