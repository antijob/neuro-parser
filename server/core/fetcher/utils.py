import logging
from typing import Optional
import aiohttp
import re
from asgiref.sync import sync_to_async
from exceptions import BadCodeException, ClientError


from user_agent import session_random_headers

from server.apps.core.models import Article, Source
from server.core.article_parser import ArticleParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetcher_session() -> aiohttp.ClientSession:
    return aiohttp.ClientSession(
        trust_env=True,
        connector=aiohttp.TCPConnector(ssl=False),
        headers=session_random_headers(),
    )


def prepare_article_url(url: str) -> str:
    if url.startswith("https://t.me/"):
        if re.search(r"[\?&]embed=1", url):
            return url
        elif "?" not in url:
            return url + "?embed=1"
        else:
            return url + "&embed=1"
    return url


def prepare_source_url(url: str) -> str:
    if re.match(r"https://t\.me/", url) and "/s/" not in url:
        url = url.replace("https://t.me/", "https://t.me/s/")
    return url


async def fetch_url(session: aiohttp.ClientSession, url: str) -> tuple[str, str]:
    async with session.get(url, allow_redirects=True) as response:
        if response.ok:
            return [await response.text(), str(response.url)]
        else:
            raise BadCodeException(response.status)


async def fetch_source(session: aiohttp.ClientSession, source: Source) -> Optional[str]:
    url = prepare_source_url(source.url)
    content, _ = await fetch_url(session, url)
    return content


async def fetch_article(
    session: aiohttp.ClientSession, article: Article, source: Source
) -> tuple[Article, str]:
    url = prepare_article_url(article.url)
    content, resolved_url = await fetch_url(session, url)

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

    return article, resolved_url
