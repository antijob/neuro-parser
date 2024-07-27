from selectolax.parser import HTMLParser
import re
from ..utils import convert_date_format, get_first_sentence

from .base_parser import ArticleData, ParserBase


class VkParser(ParserBase):
    @classmethod
    def can_handle(cls, url: str) -> bool:
        return re.match(r"https://vk\.com/", url)

    @classmethod
    def parse_raw_data(cls, data) -> ArticleData:
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

        return ArticleData(title, text, date)
