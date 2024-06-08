from lxml import etree
import requests
from ..user_agent import random_headers
from lxml.html.clean import Cleaner

from types import List
from .parsers.base_parser import ParserBase

from .parsers.vk_parser import VkParser
from .parsers.ok_parser import OkParser
from .parsers.tg_parser import TgParser
from .parsers.common_parser import CommonParser
from .parsers.rss_parser import RssParser


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


def decoded(response: requests.Response) -> str:
    encodings = ("utf-8", "cp1251", "cp866", "koi8-r")
    for encoding in encodings:
        try:
            return response.content.decode(encoding)
        except UnicodeDecodeError:
            pass
    return ""


def get_document(url: str, clean=False):
    """Get document by given url,
    cleans it if clean = True and return etree document
    """
    headers = random_headers()
    response: requests.Response
    try:
        if url.startswith("https://t.co/"):
            response = requests.get(url)
        else:
            response = requests.get(url, headers=headers, timeout=8)
    except requests.exceptions.RequestException:
        return
    if not response.status_code == 200:
        return
    html = decoded(response)
    html = html.replace("\xa0", " ")
    if html and clean:
        html = CLEANER.clean_html(html)
    try:
        document = etree.HTML(html)
    except ValueError:
        document = etree.HTML(response.content)

    if document is not None:
        document.set("url", response.url)

    return document


class SourceParser:
    parsers = [VkParser, OkParser, TgParser]
    document_parsers = [RssParser, CommonParser]

    @classmethod
    def extract_all_news_urls(cls, url: str) -> list[str]:
        for parser in cls.parsers:
            if parser.can_handle(url):
                return parser.extract_urls(url)

        document = get_document(url)
        if document is None:
            return

        for parser in cls.document_parsers:
            if parser.can_handle(url):
                return parser.extract_urls(url, document)
        raise ValueError("No suitable parser found")
