from typing import Iterable

import requests
from selectolax.parser import HTMLParser
import re
from server.libs.user_agent import random_headers
from ..utils import convert_date_format, get_first_sentence

from server.core.parser.parsers.base_parser import ArticleData, ParserBase


class OkParser(ParserBase):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return re.match(r"https://ok\.ru/", url)

    @classmethod
    def get_page_data(cls, url: str) -> ArticleData:
        page = requests.get(url, headers=random_headers())
        return cls.parse_raw_data(page.text, url)

    @classmethod
    def parse_raw_data(cls, url: str, data) -> ArticleData:
        tree = HTMLParser(data)
        text = tree.css_first("div.media-text_cnt_tx").text()
        if text:
            title = text.split(sep="\n")[0]
            if len(title) > 100:
                title = get_first_sentence(text)
        else:
            title = ""
        node = tree.css_first("div.ucard_add-info_i")
        date = ""
        if node:
            date = convert_date_format(node.text())
        return ArticleData(title, text, date, url)

    @classmethod
    def extract_urls(cls, url: str, document=None) -> Iterable[str]:
        page = requests.get(url, headers=random_headers())
        tree = HTMLParser(page.text)

        for node in tree.css("a.media-text_a"):
            news_page_link = "https://ok.ru" + node.attributes["href"]
            yield news_page_link
