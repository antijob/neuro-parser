import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

import aiohttp
from asgiref.sync import sync_to_async
from django.utils import timezone

from server.apps.core.models import Proxy

logger = logging.getLogger(__name__)


class ProxyErrorType(Enum):
    CONNECTION_ERROR = "connection_error"
    TIMEOUT = "timeout"
    AUTH_ERROR = "authentication_error"
    BAD_RESPONSE = "bad_response"
    UNKNOWN = "unknown_error"


@dataclass(frozen=True)
class ProxyData:
    """Data class representing proxy configuration."""

    url: Optional[str] = None
    login: Optional[str] = None
    password: Optional[str] = None
    error_msg: Optional[str] = None
    error_type: Optional[ProxyErrorType] = None
    last_check: Optional[float] = None

    @property
    def is_valid(self) -> bool:
        """Check if proxy data is valid."""
        return bool(self.url and not self.error_msg)


class ProxyValidator:
    """Handles proxy validation with multiple test URLs."""

    TEST_URLS = [
        "https://example.com",
        "https://httpbin.org/get",
        "https://api.ipify.org?format=json",
    ]

    TIMEOUT_SECONDS = 30
    MAX_RETRIES = 2
    RETRY_DELAY = 1

    @classmethod
    async def validate_proxy(
        cls, proxy_url: str, proxy_login: str, proxy_pass: str
    ) -> Dict:
        results = []

        for url in cls.TEST_URLS:
            for attempt in range(cls.MAX_RETRIES):
                try:
                    result = await cls._test_proxy_url(
                        proxy_url, proxy_login, proxy_pass, url
                    )
                    results.append(
                        {"success": True, "url": url, "attempt": attempt + 1}
                    )
                    break

                except aiohttp.ClientError as e:
                    error_type = cls._categorize_error(e)
                    if attempt == cls.MAX_RETRIES - 1:
                        results.append(
                            {
                                "success": False,
                                "url": url,
                                "error_type": error_type,
                                "error_msg": str(e),
                                "attempt": attempt + 1,
                            }
                        )
                    await asyncio.sleep(cls.RETRY_DELAY)

        return cls._analyze_results(results)

    @classmethod
    async def _test_proxy_url(
        cls, proxy_url: str, proxy_login: str, proxy_pass: str, test_url: str
    ) -> bool:
        timeout = aiohttp.ClientTimeout(total=cls.TIMEOUT_SECONDS)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            proxy_auth = aiohttp.BasicAuth(login=proxy_login, password=proxy_pass)
            async with session.get(
                test_url,
                allow_redirects=True,
                proxy=proxy_url,
                proxy_auth=proxy_auth,
            ) as response:
                if not response.ok:
                    raise aiohttp.ClientError(f"Bad response status: {response.status}")
                return True

    @staticmethod
    def _categorize_error(error: Exception) -> ProxyErrorType:
        error_str = str(error).lower()

        if isinstance(error, asyncio.TimeoutError):
            return ProxyErrorType.TIMEOUT
        elif "unauthorized" in error_str or "authentication" in error_str:
            return ProxyErrorType.AUTH_ERROR
        elif "connection" in error_str:
            return ProxyErrorType.CONNECTION_ERROR
        elif "bad response" in error_str:
            return ProxyErrorType.BAD_RESPONSE
        return ProxyErrorType.UNKNOWN

    @staticmethod
    def _analyze_results(results: List[Dict]) -> Dict:
        successful_tests = [r for r in results if r["success"]]
        failed_tests = [r for r in results if not r["success"]]

        if not successful_tests:
            worst_error = failed_tests[0]
            return {
                "is_valid": False,
                "error_type": worst_error["error_type"],
                "error_msg": worst_error["error_msg"],
            }

        return {"is_valid": True, "success_rate": len(successful_tests) / len(results)}


class ProxyManager:
    """Enhanced proxy manager with better error handling and validation."""

    RECHECK_INTERVAL = 300  # 5 minutes

    @classmethod
    async def get_proxy(cls) -> ProxyData:
        try:
            proxy = await sync_to_async(
                lambda: Proxy.objects.filter(is_active=True)
                .order_by("last_check", "?")
                .first()
            )()

            if proxy is None:
                return ProxyData(error_msg="No active proxies found in database")

            # Check if we need to revalidate
            current_time = timezone.now()
            if (
                proxy.last_check
                and (current_time - proxy.last_check).total_seconds()
                < cls.RECHECK_INTERVAL
                and proxy.is_active
            ):
                return ProxyData(
                    url=f"http://{proxy.ip}:{proxy.port}",
                    login=proxy.login,
                    password=proxy.password,
                    last_check=proxy.last_check.timestamp(),
                )

            proxy_url = f"http://{proxy.ip}:{proxy.port}"
            validation_result = await ProxyValidator.validate_proxy(
                proxy_url, proxy.login, proxy.password
            )

            if validation_result["is_valid"]:
                await sync_to_async(
                    lambda: Proxy.objects.filter(id=proxy.id).update(
                        is_active=True, last_check=current_time
                    )
                )()

                return ProxyData(
                    url=proxy_url,
                    login=proxy.login,
                    password=proxy.password,
                    last_check=current_time.timestamp(),
                )
            else:
                await sync_to_async(
                    lambda: Proxy.objects.filter(id=proxy.id).update(
                        is_active=False,
                        error_type=validation_result["error_type"].value,
                        error_message=validation_result["error_msg"],
                        last_check=current_time,
                    )
                )()

                return ProxyData(
                    error_msg=validation_result["error_msg"],
                    error_type=validation_result["error_type"],
                )

        except Exception as e:
            logger.error(f"Error while getting proxy: {str(e)}", exc_info=True)
            return ProxyData(
                error_msg=f"Unexpected error: {str(e)}",
                error_type=ProxyErrorType.UNKNOWN,
            )
