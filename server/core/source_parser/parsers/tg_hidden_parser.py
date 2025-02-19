from typing import Iterable, Optional
from django.utils import timezone

from server.apps.core.models import Article
from .base_parser import ParserBase, Source


class TgHiddenParser(ParserBase):
    @classmethod
    def can_handle(cls, source: Source) -> bool:
        return source.is_tg_hidden

    @classmethod
    def extract_urls(cls, source: Source, messages: list[str]) -> Iterable[Article]:
        res = []
        for url, message in messages.items():
            article = parse_message_to_article(source, url, message)
            if not article:
                continue
            res.append(article)

        return res


def parse_message_to_article(source: Source, url: str, message) -> Optional[Article]:
    try:
        text = message.message
        title = text[:100] if text else ""
        # Use the message date, not the source date
        publication_date = message.date
        is_duplicate = text is None or len(text) == 0

        # Create an Article object
        article = Article(
            title=title,
            text=text,
            publication_date=publication_date,
            url=url,  # Use the message URL instead of source URL
            is_downloaded=True,
            is_duplicate=is_duplicate,
            source=source,
        )

        return article
    except Exception as e:
        print(e)
        return None
