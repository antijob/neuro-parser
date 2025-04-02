import asyncio
import logging

from server.apps.core.models import Article, Source

from .clients import ClientFactory
from .libs.statistics import CoroutineStatistics
from .libs.exceptions import BadCodeException

from asgiref.sync import sync_to_async


# Configure logging
logger = logging.getLogger(__name__)


async def fetch_source_articles(source: Source, articles: list[Article]):
    rps: float = 1
    if ".ok.ru" in source.url or "t.me" in source.url:
        rps = 0.1

    articles_length = len(articles)
    logger.info(f"Start task. Source {source.url}: {articles_length} articles")
    statistics = CoroutineStatistics(source.url, articles_length)
    articles_to_update = []
    articles_to_create = []
    
    async with await ClientFactory.get_client(source) as client:
        delay = 1 / rps

        for article in articles:
            try:
                # Получаем и обрабатываем статью, но не сохраняем
                await client.get_article(article, source, articles_to_create)
                articles_to_update.append(article)
                
                statistics.fetch()
                await asyncio.sleep(delay)
            except BadCodeException as e:
                statistics.bad_code(e.code)
            except Exception as e:
                logger.error(f"Task {source.url}: {article.url} exception: {e}")
                statistics.exception()
    
    # Обновляем все статьи одним запросом
    if articles_to_update:
        await sync_to_async(Article.objects.bulk_update, thread_sensitive=True)(
            articles_to_update,
            ['source_id', 'title', 'text', 'is_downloaded', 'is_parsed', 
             'is_incident_created', 'is_duplicate', 'duplicate_url', 
             'is_redirect', 'is_incorrect', 'redirect_url', 'rate', 
             'incident_id', 'create_date', 'publication_date']
        )
    
    # Создаем новые статьи одним запросом
    if articles_to_create:
        await sync_to_async(Article.objects.bulk_create, thread_sensitive=True)(
            articles_to_create
        )
    
    logger.info(f"Task finished. Statistics: {statistics}")
    return statistics._fetch