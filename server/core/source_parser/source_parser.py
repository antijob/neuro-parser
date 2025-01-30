from typing import Union

import logging
from .parsers.base_parser import ParserBase

from .parsers.vk_parser import VkParser
from .parsers.ok_parser import OkParser
from .parsers.tg_parser import TgParser
from .parsers.common_parser import CommonParser
from .parsers.rss_parser import RssParser
from .parsers.tg_hidden_parser import TgHiddenParser


from server.apps.core.models import Article, Source
from server.libs.handler import HandlerRegistry

from asgiref.sync import sync_to_async


# Configure logging
logger = logging.getLogger(__name__)


async def add_articles(
    source: Source, articles: list[Union[str, Article]]
) -> list[Article]:
    added_articles: list[Article] = []
    added_urls: set[str] = set()

    for article in articles:
        if isinstance(article, Article):
            url = article.url
            article = article
        else:
            url = article
            article = Article(url=url, source=source)

        if url in added_urls:
            continue

        if not await sync_to_async(Article.objects.filter(url=url).exists)():
            added_articles.append(article)
            added_urls.add(url)

    return added_articles


class SourceParser:
    registry = HandlerRegistry[ParserBase]()
    registry.register(TgHiddenParser)
    registry.register(VkParser)
    registry.register(OkParser)
    registry.register(TgParser)
    registry.register(RssParser)
    registry.register(CommonParser)

    @classmethod
    async def create_new_articles(cls, source: Source, data: str) -> int:
        if not data:  # Return early if we have no data
            logger.warning(f"No data received for source {source.url}")
            return 0

        parser = cls.registry.choose(source)
        articles = parser.extract_urls(source.url, data)
        if not articles:
            return 0

        added = await add_articles(source, articles)
        for article in added:
            try:
                await sync_to_async(article.save)()
            except Exception as e:
                logger.exception(
                    f"When adding articles with {article.url} exception occurred: {e}"
                )
        return len(added)
