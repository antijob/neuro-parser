import logging
from typing import Optional, List

import aiohttp

from server.apps.core.models import Article, Source
from server.core.article_parser import ArticleParser
from server.core.fetcher.libs.exceptions import BadCodeException
from server.core.fetcher.libs.url_preparer import URLPreparer
from server.core.fetcher.libs.user_agent import session_random_headers

from .base_client import ClientBase

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class HttpClient(ClientBase):
    def __init__(
        self,
        proxy: Optional[str] = None,
        login: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.proxy = proxy
        self.proxy_login = login
        self.proxy_password = password
        logger.info(
            f"HttpClient initialized with proxy: {proxy}, login: {login}, password: {'*' * len(password) if password else None}"
        )

    @staticmethod
    def session() -> aiohttp.ClientSession:
        headers = session_random_headers()
        logger.debug(f"Creating new session with headers: {headers}")
        return aiohttp.ClientSession(
            trust_env=True,
            connector=aiohttp.TCPConnector(
                ssl=False,
                force_close=True,
                enable_cleanup_closed=True,
                ttl_dns_cache=300,
            ),
            timeout=aiohttp.ClientTimeout(total=30, connect=10),
            headers=headers,
            # Enable automatic decompression including brotli
            auto_decompress=True,
        )

    async def __aenter__(self):
        self._session = self.session()
        logger.info("Entered HttpClient context")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        logger.info("Exiting HttpClient context")
        await self._session.__aexit__(exc_type, exc_value, traceback)

    async def get(self, url: str) -> tuple[str, str]:
        logger.info(f"Sending request to {url}")
        logger.debug(
            f"Proxy settings: {self.proxy}, {self.proxy_login}, {self.proxy_password}"
        )

        if self.proxy is not None:
            proxy_url = self.proxy
            logger.info(f"Using proxy: {proxy_url}")
        else:
            proxy_url = None
            logger.info("No proxy specified")

        if (self.proxy_login is not None) and (self.proxy_password is not None):
            proxy_auth = aiohttp.BasicAuth(
                login=self.proxy_login, password=self.proxy_password
            )
            logger.info("Using proxy authentication")
        else:
            proxy_auth = None
            logger.info("No proxy authentication specified")

        try:
            async with self._session.get(
                url,
                allow_redirects=True,
                proxy=proxy_url,
                proxy_auth=proxy_auth,
            ) as response:
                logger.info(f"Received response with status code: {response.status}")
                logger.debug(f"Final URL: {response.url}")

                if response.ok:
                    # Try to get encoding from response headers
                    encoding = response.charset or 'utf-8'
                    try:
                        content = await response.text(encoding=encoding)
                    except UnicodeDecodeError:
                        # If that fails, try common Russian encodings
                        for enc in ['utf-8', 'windows-1251', 'cp1251', 'koi8-r']:
                            try:
                                content = await response.text(encoding=enc)
                                logger.info(f"Successfully decoded content using {enc} encoding")
                                break
                            except UnicodeDecodeError:
                                continue
                        else:
                            raise UnicodeDecodeError(f"Failed to decode content with any common encoding")
                    
                    logger.debug(f"Response body (first 500 chars): {content[:500]}...")
                    return [content, str(response.url)]
                else:
                    logger.info(f"Request failed with status code: {response.status}")
                    raise BadCodeException(response.status)
        except Exception as e:
            logger.info(f"An error occurred during the request: {str(e)}")
            raise

    async def get_article(self, article: Article, source: Source, articles_to_create: List[Article] = None) -> Article:
        logger.info(f"Getting article: {article.url}")
        url = URLPreparer.article(article.url)
        content, resolved_url = await self.get(url)

        if url != resolved_url:
            logger.info(f"Article URL redirected from {url} to {resolved_url}")
            article.redirect_url = resolved_url
            article.is_redirect = True

            new_article = Article(url=resolved_url, source=source)
            if articles_to_create is not None:
                articles_to_create.append(new_article)
            article = new_article

        logger.info("Postprocessing article")
        ArticleParser.postprocess_article(article, content)
        article.is_downloaded = True

        return article

    async def get_source(self, source: Source) -> Optional[str]:
        logger.info(f"Getting source: {source.url}")
        url = URLPreparer.source(source.url)
        content, _ = await self.get(url)
        return content
