from .base_parser import ParserBase, ArticleData
from ..utils import is_correct_article_link, get_absolute_url, is_rss_link
from lxml import cssselect
import re
import feedparser


def find_rss_urls(source_url: str, document):
    if document is None:
        return []

    links = cssselect.CSSSelector("a")(document)
    links += cssselect.CSSSelector("link")(document)

    for link in links:
        url = link.get("href")
        absolute_url = get_absolute_url(source_url, url)
        if is_rss_link(absolute_url):
            yield absolute_url


def extract_rss_urls(source_url, document):
    """Extracts article urls using RSS"""
    if document is None:
        return []
    rss_urls = find_rss_urls(source_url, document)
    for rss_url in rss_urls:
        data_parsed = feedparser.parse(rss_url)
        article_urls = [art.link for art in data_parsed.entries]
        absolute_urls = (get_absolute_url(source_url, url) for url in article_urls)

        for article_url in absolute_urls:
            if is_correct_article_link(article_url):
                yield article_url


class RssParser(ParserBase):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return re.match(r"https?://.*\.(rss|xml|feed)$", url)

    @classmethod
    def get_page_data(cls, url: str) -> ArticleData:
        raise NotImplementedError("RSS parser does not implement get_page_data")

    @classmethod
    def parse_raw_data(cls, url: str, data) -> ArticleData:
        raise NotImplementedError("RSS parser does not implement parse_raw_data")

    @classmethod
    def extract_urls(cls, url: str, document) -> list:
        return list(extract_rss_urls(url, document))
