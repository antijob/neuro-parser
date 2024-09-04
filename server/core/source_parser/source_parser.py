from typing import Iterable, Union
from .parsers.base_parser import ParserBase

from .parsers.vk_parser import VkParser
from .parsers.ok_parser import OkParser
from .parsers.tg_parser import TgParser
from .parsers.common_parser import CommonParser
from .parsers.rss_parser import RssParser

from server.apps.core.models import Article, Source
from server.core.fetcher import Fetcher
from server.libs.handler import HandlerRegistry

from asgiref.sync import sync_to_async


async def add_articles(
    source: Source, articles: list[Union[str, Article]]
) -> list[Article]:
    added = []

    for article in articles:
        if isinstance(article, Article):
            url = article.url
            article = article
        else:
            url = article
            article = Article(url=url, source=source)

        try:
            article, created = await sync_to_async(Article.objects.get_or_create)(
                url=url, source=source
            )
            if created:
                added.append(article)
        except Exception as e:
            raise type(e)(f"When adding articles with {url} exception occurred: {e}")

    return added


class SourceParser:
    registry = HandlerRegistry[ParserBase]()
    registry.register(VkParser)
    registry.register(OkParser)
    registry.register(TgParser)
    registry.register(RssParser)
    registry.register(CommonParser)

    @classmethod
    async def _extract_all_news_urls(cls, source: Source) -> Iterable[str]:
        url = source.url
        html = await Fetcher.download_source(source)
        if html is None:
            return None

        parser = cls.registry.choose(source)
        return parser.extract_urls(url, html)

    @classmethod
    async def create_new_articles(cls, source: Source) -> int:
        urls = await cls.extract_all_news_urls(source)
        if not urls:
            return 0

        added = await add_articles(source, urls)
        for article in added:
            await sync_to_async(article.save)()
        return len(added)
