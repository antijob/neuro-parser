from typing import Iterable

import requests
from selectolax.parser import HTMLParser
import re
from server.libs.user_agent import random_headers
from ..utils import convert_date_format, get_first_sentence

from server.core.parser.parsers.base_parser import ArticleData, ParserBase


class VkParser(ParserBase):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return re.match(r"https://vk\.com/", url)

    @classmethod
    def parse_raw_data(cls, url: str, data) -> ArticleData:
        tree = HTMLParser(data)
        wall_post = tree.css_first("div.wall_post_text")
        text = wall_post.text() if wall_post else None
        if text:
            title = text.split(sep="\n")[0]
            if len(title) > 100:
                title = get_first_sentence(text)
        else:
            title = ""
        date = convert_date_format(
            tree.css_first("time.PostHeaderSubtitle__item").text()
        )

        return ArticleData(title, text, date, url)

    # И тут с какого хрена?
    @classmethod
    def extract_urls(cls, url: str, document=None) -> Iterable[str]:
        page = requests.get(url, headers=random_headers())
        tree = HTMLParser(page.text)

        for node in tree.css("a.PostHeaderSubtitle__link"):
            news_page_link = "https://vk.com" + node.attributes["href"]
            yield news_page_link
