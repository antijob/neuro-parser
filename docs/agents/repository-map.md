# Repository Map

Use this map by capability instead of memorizing paths.

## If You Need To...

### Add or modify a prediction category

- Update incident type domain configuration and related admin/API exposure.
- Ensure predictor behavior supports the category and confidence handling.
- Add tests for acceptance/rejection behavior.

### Add a source ingestion pattern

- Extend source parsing behavior for the new feed/link structure.
- Validate fetched content quality before prediction stages.
- Ensure deduplication still runs before incident planning.

### Add bot commands or callbacks

- Add handler logic in the relevant router group.
- Update inline keyboards and subscription state transitions.
- Verify notification routing remains consistent.

### Change API behavior

- Update serializers and viewsets together.
- Preserve compatibility unless intentionally versioning behavior.
- Add tests for filtering, pagination, and contract shape.

### Change scheduled processing

- Adjust Celery task chain and beat schedule definitions.
- Keep task retries and idempotency expectations explicit.
- Validate impacts on notification timing and queue throughput.

## Start Points

- System overview: [../ARCHITECTURE.md](../ARCHITECTURE.md)
- Domain concepts: [../DOMAIN.md](../DOMAIN.md)
- Coding conventions: [../CONVENTIONS.md](../CONVENTIONS.md)
