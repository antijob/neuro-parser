import socket

import pytest

from server.apps.core.models import Article

from server.apps.api.validators import UnsafeURLError, validate_public_http_url


def fake_resolver(address):
    family = socket.AF_INET6 if ":" in address else socket.AF_INET

    def resolve(host, port, proto=0):
        return [(family, socket.SOCK_STREAM, proto, "", (address, port or 0))]

    return resolve


def test_public_address_accepted(monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", fake_resolver("93.184.216.34"))
    assert validate_public_http_url("https://example.com/a") == "https://example.com/a"


@pytest.mark.parametrize(
    "url",
    ["file:///etc/passwd", "ftp://example.com/x", "http:///nohost", "example.com"],
)
def test_bad_scheme_rejected(url):
    with pytest.raises(UnsafeURLError):
        validate_public_http_url(url)


@pytest.mark.parametrize(
    "address",
    [
        "127.0.0.1",
        "10.0.0.1",
        "169.254.169.254",
        "192.168.1.1",
        "::1",
        "::ffff:127.0.0.1",
    ],
)
def test_non_public_address_rejected(monkeypatch, address):
    monkeypatch.setattr(socket, "getaddrinfo", fake_resolver(address))
    with pytest.raises(UnsafeURLError):
        validate_public_http_url("http://internal.example/")


@pytest.mark.django_db
def test_fetch_rejects_internal_url_without_creating_article(staff_client, monkeypatch):
    monkeypatch.setattr(socket, "getaddrinfo", fake_resolver("127.0.0.1"))
    response = staff_client.post(
        "/api/articles/by_url/fetch/", {"url": "http://x.example/"}
    )
    assert response.status_code == 400
    assert not Article.objects.filter(url="http://x.example/").exists()


@pytest.mark.django_db
def test_fetch_rejects_file_scheme(staff_client):
    response = staff_client.post(
        "/api/articles/by_url/fetch/", {"url": "file:///etc/passwd"}
    )
    assert response.status_code == 400
    assert not Article.objects.filter(url="file:///etc/passwd").exists()
