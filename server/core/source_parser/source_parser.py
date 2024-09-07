from typing import Iterable, Optional
from .parsers.base_parser import ParserBase

import re
from lxml.html.clean import Cleaner
from selectolax.parser import HTMLParser


from .parsers.vk_parser import VkParser
from .parsers.ok_parser import OkParser
from .parsers.tg_parser import TgParser
from .parsers.common_parser import CommonParser
from .parsers.rss_parser import RssParser

from server.apps.core.models import Article, Source
from server.core.fetcher import Fetcher
from server.libs.handler import HandlerRegistry

from asgiref.sync import async_to_sync


CLEANER = Cleaner(
    scripts=True,
    javascript=True,
    comments=True,
    style=True,
    links=True,
    meta=True,
    add_nofollow=False,
    page_structure=True,
    processing_instructions=True,
    embedded=True,
    frames=True,
    forms=True,
    annoying_tags=True,
    kill_tags=["img", "noscript", "button"],
    remove_unknown_tags=True,
    safe_attrs_only=False,
)


async def get_source_data(source: Source) -> Optional[str]:
    """Get document by given url"""
    html = await Fetcher.download_source(source)
    if html:
        html = html.replace("\xa0", " ")
    return html


def build_document(html, clean=False):
    """
    Return etree document
    cleans it if clean = True
    """
    if not html:
        return None
    if clean:
        html = CLEANER.clean_html(html)
    try:
        document = HTMLParser(html)
    except ValueError:
        pass

    return document


def add_articles(source: Source, urls: list[str]) -> list[Article]:
    pattern = re.compile(r"https?://(?P<url_without_method>.+)")
    added = []

    for url in urls:
        match = pattern.match(url)
        if not match:
            continue

        url_without_method = match.group("url_without_method")

        if not Article.objects.filter(url__iendswith=url_without_method).exists():
            try:
                added.append(Article.objects.create(url=url, source=source))
            except Exception as e:
                raise type(e)(
                    f"When adding articles with {url} exception occurred: {e}"
                )

    return added


class SourceParser:
    registry = HandlerRegistry[ParserBase]()
    registry.register(VkParser)
    registry.register(OkParser)
    registry.register(TgParser)
    registry.register(RssParser)
    registry.register(CommonParser)

    @classmethod
    async def extract_all_news_urls(cls, source: Source) -> Iterable[str]:
        url = source.url
        html = await get_source_data(source)
        if html is None:
            return None

        document = build_document(html, clean=True)
        parser = cls.registry.choose(url)
        return parser.extract_urls(url, document)

    @classmethod
    def create_new_articles(cls, source: Source) -> int:
        urls = async_to_sync(cls.extract_all_news_urls)(source)
        if not urls:
            return 0
        added = add_articles(source, urls)
        return len(added)
