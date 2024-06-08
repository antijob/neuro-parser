from types import List

from selectolax.parser import HTMLParser
import requests
import re
from datetime import datetime

# from ..utils import get_first_sentence

from server.core.parser.parsers.base_parser import ArticleData, ParserBase


def get_first_sentence(text):
    pattern = r"^(.*?[.!?])\s"
    match = re.search(pattern, text)

    if match:
        first_sentence = match.group(1)
        return first_sentence.strip()
    else:
        return text.strip()


class TgParser(ParserBase):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return re.match(r"https://t\.me/", url)

    @classmethod
    def get_page_data(cls, url: str) -> ArticleData:
        params = {"embed": "1"}
        page = requests.get(url, params)
        return cls.parse_raw_data(page.text, url)

    @classmethod
    def parse_raw_data(cls, url: str, data) -> ArticleData:
        tree = HTMLParser(data)
        text_tag = tree.css_first("div.tgme_widget_message_text")
        if text_tag is not None:
            text = text_tag.text()
            title = text.split(sep="\n")[0]
            if len(title) > 100:
                title = get_first_sentence(text)
        else:
            text = ""
            title = ""

        time_tag = tree.css_first("time.datetime")
        date_time = time_tag.attributes["datetime"]
        original_datetime = datetime.fromisoformat(date_time)
        date = original_datetime.strftime("%Y-%m-%d")
        return ArticleData(title, text, date, url)

    @classmethod
    def extract_urls(cls, url: str, document=None) -> List[str]:
        if "/s/" not in url:
            url = url.replace("https://t.me/", "https://t.me/s/")
        page = requests.get(url)
        tree = HTMLParser(page.text)

        for node in tree.css("a.tgme_widget_message_date"):
            yield node.attributes["href"]
