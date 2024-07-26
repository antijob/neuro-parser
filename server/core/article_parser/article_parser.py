import logging
from typing import Any
from .parsers.base_parser import ArticleData, ParserBase
from .parsers.tg_parser import TgParser
from .parsers.vk_parser import VkParser
from .parsers.ok_parser import OkParser
from .parsers.common_parser import CommonParser
from server.apps.core.models import Article
import datetime
from asgiref.sync import sync_to_async

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArticleParser:
    parsers: list[ParserBase] = [VkParser, OkParser, TgParser, CommonParser]

    @classmethod
    def parse_article_raw_data(cls, url: str, data) -> ArticleData:
        try:
            for parser in cls.parsers:
                if parser.can_handle(url):
                    return parser.parse_raw_data(data)
            raise ValueError("No suitable parser found")
        except Exception as e:
            logger.error(f"Error parsing article raw data from URL {url}: {e}")
            raise

    @classmethod
    async def postprocess_article(cls, article: Article, data: Any) -> None:
        try:
            article_data: ArticleData = cls.parse_article_raw_data(article.url, data)
            if article_data:
                article.title, article.text, publication_date = article_data
                if publication_date:
                    article.publication_date = publication_date
                else:
                    article.publication_date = datetime.date.today()
            article.is_downloaded = True
            await sync_to_async(article.save, thread_sensitive=True)()
        except ValueError as e:
            logger.warning(f"Value error during postprocessing of article {article.url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during postprocessing of article {article.url}: {e}")

