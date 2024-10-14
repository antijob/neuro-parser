from typing import Optional
import aiohttp
from asgiref.sync import sync_to_async
from server.core.fetcher.libs.exceptions import BadCodeException


from server.core.fetcher.libs.user_agent import session_random_headers
from server.core.fetcher.libs.url_preparer import URLPreparer

from server.apps.core.models import Article, Source
from server.core.article_parser import ArticleParser


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
        await self._session.__aexit__(exc_type, exc_value, traceback)

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
        article.is_downloaded = True
        await sync_to_async(article.save, thread_sensitive=True)()

        return article

    async def get_source(self, source: Source) -> Optional[str]:
        url = URLPreparer.source(source.url)
        content, _ = await self.get(url)
        return content
