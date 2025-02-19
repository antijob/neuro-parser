from server.apps.core.models import Article, Source
from server.core.fetcher.clients.telethon_client import TelethonClient


TELEGRAM_API_ID = "YOUR API ID"
TELEGRAM_API_HASH = "YOUR API HASH"

source = Source(url="https://t.me/ArzamasLive")
client = TelethonClient(TELEGRAM_API_ID, TELEGRAM_API_HASH)

client.init_session()
res = None

async def get_source():
    global res, client
    async with client as client:
        res = await client.get_source(source)


client.client.loop.run_until_complete(get_source())
article = Article(url=res[0])

print(article)


article = Article(url="https://t.me/c/1579984138/23")

async def get_article():
    global res, client, article
    async with client as client:
        article = await client.get_article(article, source)
        print(article)
        print(article.title)
        print(article.text)
        print(article.publication_date)


client.client.loop.run_until_complete(get_article())
