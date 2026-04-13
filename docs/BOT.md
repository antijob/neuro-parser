# Bot

The Telegram bot is built on aiogram and is used for subscription and notification workflows.

## Responsibilities

- Manage user and channel subscription preferences
- Route command and callback interactions
- Deliver incident notifications to configured channels

## Interaction Model

- Router-based handler organization
- Inline keyboards for category and geography selection
- Service handlers for lifecycle and support operations

## Delivery Model

- Notifications are sent via asynchronous tasks.
- Retry behavior is used for transient Telegram failures.
- Throughput controls should protect from rate-limit pressure.

## Change Guidance

When introducing bot functionality:

1. Add handler and keyboard updates together.
2. Ensure subscription persistence rules stay consistent.
3. Add tests for handler logic and routing side effects.

## See Also

- Domain model: [DOMAIN.md](DOMAIN.md)
- ML pipeline: [ML.md](ML.md)
- Agent repository map: [agents/repository-map.md](agents/repository-map.md)
