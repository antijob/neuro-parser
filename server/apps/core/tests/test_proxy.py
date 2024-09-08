import pytest
from server.apps.core.models import Proxy, Country
from server.core.fetcher.libs.proxy import ProxyManager


@pytest.fixture
def setup_proxies():
    country = Country.objects.create(name="RUS")
    Proxy.objects.create(ip="192.168.1.1", port=8080, country=country)
    Proxy.objects.create(ip="10.0.0.1", port=3128, country=country)
    return ["192.168.1.1:8080", "10.0.0.1:3128"]


@pytest.mark.django_db
def test_get_proxies(setup_proxies):
    proxy_manager = ProxyManager()
    proxies = proxy_manager._get_proxies()
    assert set(proxies) == set(setup_proxies)


@pytest.mark.django_db
def test_get_proxy(setup_proxies):
    proxy = ProxyManager.get_proxy()
    assert proxy in setup_proxies


@pytest.mark.django_db
def test_get_proxy_with_no_proxies():
    Proxy.objects.all().delete()
    with pytest.raises(IndexError):
        ProxyManager.get_proxy()
