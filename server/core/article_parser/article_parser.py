import logging
import re
from typing import Any
import datetime
from server.settings.components.predict import INCORRECT_ARTICLE_LENGTH

from .parsers.base_parser import ArticleData, ParserBase
from .parsers.tg_parser import TgParser
from .parsers.vk_parser import VkParser
from .parsers.ok_parser import OkParser
from .parsers.common_parser import CommonParser
from server.apps.core.models import Article
from server.libs.handler import HandlerRegistry


# Configure logging
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
                # Сначала обновляем текст и другие поля
                article.title, article.text, publication_date = article_data
                if publication_date:
                    article.publication_date = publication_date
                else:
                    article.publication_date = datetime.date.today()
                    
                # Теперь проверяем корректность текста
                article.is_incorrect = cls.article_is_incorrect(article)
                
        except ValueError as e:
            logger.warning(
                f"Value error during postprocessing of article {article.url}: {e}"
            )
        except Exception as e:
            logger.error(
                f"Unexpected error during postprocessing of article {article.url}: {e}"
            )

    @classmethod
    def article_is_incorrect(cls, article: Article) -> bool:
        """
        Проверяет статью на корректность по длине текста.
        
        Args:
            article: статья для проверки
            
        Returns:
            bool: True если статья некорректна (слишком короткая), False если корректна
        """
        text = article.text
        if not text or len(text) < INCORRECT_ARTICLE_LENGTH:
            return True
        return False