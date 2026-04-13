# Architecture

This project processes articles from media sources, predicts incident relevance, and notifies Telegram subscribers.

## Runtime Topology

- Django web application for admin, API, and integrations
- Celery workers for crawling, parsing, and bot notifications
- Celery beat for scheduled pipelines
- PostgreSQL for persistent relational data
- Redis for queueing and caching
- Traefik and Flower for routing and task visibility in local and deployment setups

## Functional Domains

- API domain: REST access for incidents, sources, and articles
- Core domain: source ingestion, article parsing, deduplication, prediction orchestration
- Bot domain: Telegram subscriptions, routing, and outbound notifications
- User domain: authentication and account-level behavior

## Processing Flow

1. Sources are crawled on schedule.
2. Candidate links are fetched and article content is extracted.
3. Parsed articles are normalized and deduplicated.
4. Predictors evaluate article text against active incident types.
5. Accepted incidents are persisted and routed to subscribed Telegram channels.

## Architectural Intent

- Keep ingestion, parsing, and prediction separated by responsibility.
- Keep asynchronous workloads in Celery to protect web request latency.
- Keep domain entities stable and push provider-specific logic to boundaries.
- Favor predictable, explicit flows that are easy for humans and agents to inspect.

## See Also

- Domain model: [DOMAIN.md](DOMAIN.md)
- ML pipeline: [ML.md](ML.md)
- Bot behavior: [BOT.md](BOT.md)
- API behavior: [API.md](API.md)
