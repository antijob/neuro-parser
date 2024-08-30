from typing import Iterable, Union
from .parsers.base_parser import ParserBase

import re

from .parsers.vk_parser import VkParser
from .parsers.ok_parser import OkParser
from .parsers.tg_parser import TgParser
from .parsers.common_parser import CommonParser
from .parsers.rss_parser import RssParser
from .parsers.tg_hidden_parser import TgHiddenParser

from server.apps.core.models import Article, Source
from server.core.fetcher import Fetcher

from asgiref.sync import sync_to_async


async def add_articles(
    source: Source, articles: list[Union[str, Article]]
) -> list[Article]:
    pattern = re.compile(r"https?://(?P<url_without_method>.+)")
    added = []

    for article in articles:
        if isinstance(article, Article):
            url = article.url
            article = article
        else:
            url = article
            article = Article(url=url, source=source)

        match = pattern.match(url)
        if not match:
            continue

        url_without_method = match.group("url_without_method")
        # unefficient:
        if not await sync_to_async(
            Article.objects.filter(url__iendswith=url_without_method).exists
        )():
            added.append(article)

    return added


class SourceParser:
    parsers: list[ParserBase] = [
        TgHiddenParser,
        VkParser,
        OkParser,
        TgParser,
        RssParser,
        CommonParser,
    ]

    @classmethod
    async def extract_all_news_urls(
        cls, source: Source
    ) -> Iterable[Union[str, Article]]:
        url = source.url
        html = await Fetcher.download_source(source)
        if html is None:
            return None

        for parser in cls.parsers:
            if parser.can_handle(source):
                return parser.extract_urls(url, html)
        raise ValueError("No suitable parser found")

    @classmethod
    async def create_new_articles(cls, source: Source) -> int:
        urls = await cls.extract_all_news_urls(source)
        if not urls:
            return 0
        added = await add_articles(source, urls)
        print("Articles from source parser:", added)
        for article in added:
            await sync_to_async(article.save)()
        return len(added)
