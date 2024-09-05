from django.test import TestCase
from server.apps.core.models import Proxy, Country
from server.core.fetcher.libs.proxy import (
    ProxyManager,
)


class ProxyManagerTestCase(TestCase):
    def setUp(self):
        # Создаем тестовые данные
        default_country = Country.objects.get(name="RUS")
        Proxy.objects.create(ip="192.168.1.1", port=8080, country=default_country)
        Proxy.objects.create(ip="10.0.0.1", port=3128, country=default_country)

    def test_get_proxies(self):
        proxy_f = ProxyManager()
        proxies = proxy_f._get_proxies()
        print(proxies, type(proxies))
        self.assertEqual(len(proxies), 2)
        self.assertIn("192.168.1.1:8080", proxies)
        self.assertIn("10.0.0.1:3128", proxies)

    def test_get_proxy(self):
        proxy = ProxyManager.get_proxy()
        self.assertIn(proxy, ["192.168.1.1:8080", "10.0.0.1:3128"])

    def test_get_proxy_with_no_proxies(self):
        Proxy.objects.all().delete()
        with self.assertRaises(IndexError):
            ProxyManager.get_proxy()
