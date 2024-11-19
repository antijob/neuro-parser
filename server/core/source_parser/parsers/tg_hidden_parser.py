from typing import Iterable, Optional

from server.apps.core.models import Article
from .base_parser import ParserBase, Source


class TgHiddenParser(ParserBase):
    @classmethod
    def can_handle(cls, source: Source) -> bool:
        return source.is_tg_hidden

    @classmethod
    def extract_urls(cls, url: str, messages: list[str]) -> Iterable[Article]:
        res = []
        for url, message in messages.items():
            article = parse_message_to_article(url, message)
            if not article:
                continue
            res.append(article)

        return res


def parse_message_to_article(url: str, message) -> Optional[Article]:
    try:
        text = message.message
        title = text[:100]
        publication_date = message.date
        is_duplicate = text is None or len(text) == 0

        # Create an Article object
        article = Article(
            title=title,
            text=text,
            publication_date=publication_date,
            url=url,
            is_downloaded=True,
            is_duplicate=is_duplicate,
        )

        return article
    except Exception as e:
        print(e)
        return None
