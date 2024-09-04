from typing import Iterable
import re
from .base_parser import ParserBase, Source
from ..utils import is_correct_article_link, get_absolute_url, is_rss_link
import feedparser

from ..utils import build_document


def find_rss_urls(source_url: str, document) -> Iterable[str]:
    if document is None:
        return []

    links = document.css("a")
    links += document.css("link")

    for link in links:
        url = link.attributes.get("href")
        if url:
            absolute_url = get_absolute_url(source_url, url)
            if is_rss_link(absolute_url):
                yield absolute_url


class RssParser(ParserBase):
    @classmethod
    def can_handle(cls, source: Source) -> bool:
        return re.match(r"https?://.*\.(rss|xml|feed)$", source.url) is not None

    @classmethod
    def extract_urls(cls, source_url: str, document=None) -> Iterable[str]:
        if document is None:
            return []

        document = build_document(document, clean=True)

        rss_urls = find_rss_urls(source_url, document)
        for rss_url in rss_urls:
            data_parsed = feedparser.parse(rss_url)
            article_urls = [art.link for art in data_parsed.entries]
            absolute_urls = (get_absolute_url(source_url, url) for url in article_urls)

            for article_url in absolute_urls:
                if is_correct_article_link(article_url):
                    yield article_url
