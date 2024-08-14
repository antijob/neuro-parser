import logging
from typing import Optional
import aiohttp
from asgiref.sync import sync_to_async
from exceptions import BadCodeException


from user_agent import session_random_headers
from url_preparer import URLPreparer

from server.apps.core.models import Article, Source
from server.core.article_parser import ArticleParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NPClient:
    def __init__(self):
        pass

    @staticmethod
    def session():
        return aiohttp.ClientSession(
            trust_env=True,
            connector=aiohttp.TCPConnector(ssl=False),
            headers=session_random_headers(),
        )

    async def __aenter__(self):
        self._session = self.session()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self._session.aclose()

    async def close(self):
        await self._session.aclose()

    async def get(self, url: str) -> tuple[str, str]:
        async with self._session.get(url, allow_redirects=True) as response:
            if response.ok:
                return [await response.text(), str(response.url)]
            else:
                raise BadCodeException(response.status)

    async def get_article(self, article: Article, source: Source) -> Article:
        url = URLPreparer.article(article.url)
        content, resolved_url = await self.get(url)

        if url != resolved_url:
            article.redirect_url = resolved_url
            article.is_redirect = True
            await sync_to_async(article.save, thread_sensitive=True)()

            article, _ = await sync_to_async(
                Article.objects.get_or_create, thread_sensitive=True
            )(url=resolved_url)
            article.source = source

        ArticleParser.postprocess_article(article, content)
        await sync_to_async(article.save, thread_sensitive=True)()

        return article

    async def get_source(self, source: Source) -> Optional[str]:
        url = URLPreparer.source(source.url)
        content, _ = await self.get(url)
        return content
