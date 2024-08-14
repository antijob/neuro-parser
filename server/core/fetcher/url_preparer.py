import re


class URLPreparer:
    @staticmethod
    def article(url: str) -> str:
        if url.startswith("https://t.me/"):
            if re.search(r"[\?&]embed=1", url):
                return url
            elif "?" not in url:
                return url + "?embed=1"
            else:
                return url + "&embed=1"
        return url

    @staticmethod
    def source(url: str) -> str:
        if re.match(r"https://t\.me/", url) and "/s/" not in url:
            url = url.replace("https://t.me/", "https://t.me/s/")
        return url
