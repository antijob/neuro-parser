import logging
from typing import Optional
from dataclasses import dataclass
import aiohttp
from asgiref.sync import sync_to_async
from server.apps.core.models import Proxy

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProxyData:
    """Data class representing proxy configuration."""

    url: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    error_msg: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        """Check if proxy data is valid."""
        return bool(self.url and not self.error_msg)


class ProxyError(Exception):
    """Custom exception for proxy-related errors."""

    pass


class ProxyManager:
    """Manages proxy selection and validation."""

    TIMEOUT_SECONDS = 60
    TEST_URL = "https://example.com"

    @staticmethod
    async def get_proxy() -> ProxyData:
        """
        Get and validate an active proxy from the database.
        Returns validated ProxyData or ProxyData with error message.
        """
        try:
            proxy = await sync_to_async(
                lambda: Proxy.objects.filter(is_active=True).order_by("?").first()
            )()
            logger.debug(f"Proxy from database: {proxy}")

            if proxy is None:
                return ProxyData(error_msg="No active proxies found in database")

            proxy_url = f"http://{proxy.ip}:{proxy.port}"

            if not await ProxyManager._check_proxy(
                proxy_url, proxy.login, proxy.password
            ):
                await sync_to_async(
                    lambda: Proxy.objects.filter(id=proxy.id).update(is_active=False)
                )()
                return ProxyData(error_msg=f"Proxy {proxy_url} validation failed")

            return ProxyData(url=proxy_url, login=proxy.login, password=proxy.password)

        except Exception as e:
            logger.error(f"Error while getting proxy: {str(e)}", exc_info=True)
            return ProxyData(error_msg=f"Unexpected error: {str(e)}")

    @classmethod
    async def _check_proxy(
        cls, proxy_url: str, proxy_login: str, proxy_pass: str
    ) -> bool:
        """
        Validate proxy by making a test request.
        """
        timeout = aiohttp.ClientTimeout(total=cls.TIMEOUT_SECONDS)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                proxy_auth = aiohttp.BasicAuth(login=proxy_login, password=proxy_pass)
                async with session.get(
                    cls.TEST_URL,
                    allow_redirects=True,
                    proxy=proxy_url,
                    proxy_auth=proxy_auth,
                ) as response:
                    logger.debug(f"Proxy check passed: {response.content}")
                    return response.ok

            except Exception as e:
                logger.error(f"Proxy {proxy_url} check failed: {str(e)}", exc_info=True)
                return False
