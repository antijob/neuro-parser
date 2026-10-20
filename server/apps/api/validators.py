import ipaddress
import socket
from urllib.parse import urlparse


class UnsafeURLError(ValueError):
    """Raised when a URL must not be fetched by the server."""


def validate_public_http_url(url: str) -> str:
    """Accept only http(s) URLs whose host resolves to public addresses."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise UnsafeURLError("Only http and https URLs are allowed")

    try:
        infos = socket.getaddrinfo(
            parsed.hostname, parsed.port, proto=socket.IPPROTO_TCP
        )
    except socket.gaierror:
        raise UnsafeURLError("Host cannot be resolved")

    for info in infos:
        ip = ipaddress.ip_address(info[4][0].split("%")[0])
        if ip.version == 6 and ip.ipv4_mapped:
            ip = ip.ipv4_mapped
        if not ip.is_global or ip.is_multicast:
            raise UnsafeURLError("URL points to a non-public address")
    return url
