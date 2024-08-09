import aiohttp
import re
from asgiref.sync import sync_to_async


from server.libs.user_agent import session_random_headers

from server.apps.core.models import Article, Source
from server.core.article_parser import ArticleParser


def fetcher_session() -> aiohttp.ClientSession:
    return aiohttp.ClientSession(
        trust_env=True,
        connector=aiohttp.TCPConnector(ssl=False),
        headers=session_random_headers(),
    )


def prepare_source_url(url: str) -> str:
    if re.match(r"https://t\.me/", url) and "/s/" not in url:
        url = url.replace("https://t.me/", "https://t.me/s/")
    return url


async def fetch_url(session: aiohttp.ClientSession, url: str) -> tuple[str, str]:
    params = {}
    if url.startswith("https://t.me/"):
        params = {"embed": "1"}
    try:
        async with session.get(url, params=params, allow_redirects=True) as response:
            if response.ok:
                return [await response.text(), str(response.url)]
            else:
                raise BadCodeException(response.status)
    except aiohttp.ClientError as e:
        logger.error(f"Network error occurred while fetching URL {url}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error occurred while fetching URL {url}: {e}")
        raise


async def fetch_article(
    session: aiohttp.ClientSession, article: Article, source: Source
) -> tuple[Article, str]:
    content, resolved_url = await fetch_url(session, article.url)

    if article.url != resolved_url:
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
