from aiohttp import ClientError


class BadCodeException(Exception):
    def __init__(self, code):
        super().__init__("Bad code")
        self.code = code


class ProxyException(Exception):
    """Exception raised for proxy-related errors."""

    pass
