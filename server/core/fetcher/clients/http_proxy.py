import logging
from typing import Optional, Tuple, List

import aiohttp

from server.apps.core.models import Article, Source
from server.core.article_parser import ArticleParser
from server.core.fetcher.libs.exceptions import BadCodeException, ProxyException
from server.core.fetcher.libs.proxy import ProxyData, ProxyManager
from server.core.fetcher.libs.url_preparer import URLPreparer
from server.core.fetcher.libs.user_agent import session_random_headers
from server.core.fetcher.clients.http_client import HttpClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class HttpProxyClient:
    """Enhanced HTTP client with automatic proxy management."""

    MAX_PROXY_RETRIES = 3
    REQUEST_TIMEOUT = 60

    def __init__(self, proxy_data: Optional[ProxyData] = None, use_proxy: bool = True):
        self._session: Optional[aiohttp.ClientSession] = None
        self._proxy_data = proxy_data
        self._use_proxy = use_proxy
        logger.info(
            f"HttpClient initialized with proxy_data: {proxy_data and proxy_data.url}"
        )

    @staticmethod
    def _create_session() -> aiohttp.ClientSession:
        headers = session_random_headers()
        logger.debug(f"Creating new session with headers: {headers}")
        return aiohttp.ClientSession(
            trust_env=True,
            connector=aiohttp.TCPConnector(ssl=False),
            headers=headers,
            timeout=aiohttp.ClientTimeout(total=HttpProxyClient.REQUEST_TIMEOUT),
        )

    async def __aenter__(self):
        self._session = self._create_session()
        if self._use_proxy and not self._proxy_data:
            self._proxy_data = await ProxyManager.get_proxy()
        logger.info(
            f"Entered HttpClient context with proxy: {self._proxy_data and self._proxy_data.url}"
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        logger.info("Exiting HttpClient context")
        if self._session:
            await self._session.close()

    async def _get_with_proxy_retry(
        self, url: str, retry_count: int = 0
    ) -> Tuple[str, str]:
        """Make HTTP request with proxy retry logic.
        If use_proxy is True, first tries without proxy, then with proxy on failure.
        """
        # First try without proxy if this is the first attempt
        if self._use_proxy and retry_count == 0:
            try:
                logger.info(f"Attempting direct request without proxy to: {url}")
                async with HttpClient() as client:
                    return await client.get(url)
            except (aiohttp.ClientError, BadCodeException) as e:
                logger.info(f"Direct request to {url} failed: {str(e)}. Will retry with proxy.")

        # If we need to use proxy, ensure we have valid proxy data
        if self._use_proxy:
            if not self._proxy_data or not self._proxy_data.is_valid:
                self._proxy_data = await ProxyManager.get_proxy()
                if not self._proxy_data.is_valid:
                    raise ProxyException("No valid proxy available")

        try:
            return await self._make_request(url)
        except (aiohttp.ClientError, ProxyException) as e:
            if retry_count >= self.MAX_PROXY_RETRIES:
                logger.error(f"Network error occurred while fetching URL {url}")
                raise ProxyException(f"Failed to fetch {url} after {self.MAX_PROXY_RETRIES} retries") from e

            logger.warning(
                f"Request to {url} failed with proxy {self._proxy_data.url}, retrying... ({retry_count + 1}/{self.MAX_PROXY_RETRIES})"
            )
            if self._use_proxy:
                self._proxy_data = await ProxyManager.get_proxy()
            return await self._get_with_proxy_retry(url, retry_count + 1)

    async def _make_request(self, url: str) -> Tuple[str, str]:
        """Make single HTTP request with current proxy settings."""
        proxy_settings = {}
        if self._proxy_data and self._proxy_data.is_valid:
            proxy_settings.update(
                {
                    "proxy": self._proxy_data.url,
                    "proxy_auth": (
                        aiohttp.BasicAuth(
                            login=self._proxy_data.login,
                            password=self._proxy_data.password,
                        )
                        if self._proxy_data.login and self._proxy_data.password
                        else None
                    ),
                }
            )

        async with self._session.get(
            url, allow_redirects=True, **proxy_settings
        ) as response:
            logger.info(f"Response status code: {response.status} for URL: {url}")
            if response.ok:
                content = await response.text()
                return content, str(response.url)
            raise BadCodeException(response.status)

    async def get(self, url: str) -> Tuple[str, str]:
        """Make HTTP GET request with automatic proxy management."""
        return await self._get_with_proxy_retry(url)

    async def get_article(self, article: Article, source: Source, articles_to_create: List[Article] = None) -> Article:
        """Fetch and process article content."""
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
        """Fetch source content."""
        logger.info(f"Getting source: {source.url}")
        url = URLPreparer.source(source.url)
        content, _ = await self.get(url)
        return content
