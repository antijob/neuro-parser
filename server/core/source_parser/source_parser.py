from typing import Union

import logging
from .parsers.base_parser import ParserBase

from .parsers.vk_parser import VkParser
from .parsers.ok_parser import OkParser
from .parsers.tg_parser import TgParser
from .parsers.common_parser import CommonParser
from .parsers.rss_parser import RssParser
from .parsers.tg_hidden_parser import TelethonParser


from server.apps.core.models import Article, Source
from server.libs.handler import HandlerRegistry

from asgiref.sync import sync_to_async


# Configure logging
logger = logging.getLogger(__name__)


async def add_articles(
    source: Source, articles: list[Union[str, Article]]
) -> list[Article]:
    added_articles: list[Article] = []
    all_urls: list[str] = []
    url_to_article_map = {}

    # First, collect all URLs and create a mapping
    for article in articles:
        if isinstance(article, Article):
            url = article.url
            article_obj = article
        else:
            url = article
            article_obj = Article(url=url, source=source)

        # Skip duplicates in the input list
        if url in url_to_article_map:
            continue

        all_urls.append(url)
        url_to_article_map[url] = article_obj

    # Get all existing URLs in a single query
    existing_urls = set(await sync_to_async(lambda: list(
        Article.objects.filter(url__in=all_urls).values_list('url', flat=True)
    ))())

    # Add only articles with URLs that don't exist yet
    for url, article in url_to_article_map.items():
        if url not in existing_urls:
            added_articles.append(article)

    return added_articles


class SourceParser:
    registry = HandlerRegistry[ParserBase]()
    registry.register(TelethonParser)
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
        articles = parser.extract_urls(source, data)
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
