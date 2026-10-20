# API

The API surface is built with Django REST Framework and exposes incident, source, and article data.

## API Scope

- Incident type listing and filtering
- Media incident retrieval for downstream consumers
- Source and article visibility for diagnostics and operations

## Design Notes

- Use serializers for stable payload contracts.
- Keep queryset filtering explicit and safe.
- Keep pagination and ordering in the shared DRF classes (`pagination.py`, `filters.py`); do not hand-roll `limit` or `order_by` parsing in views.

## Access Rules

- Every endpoint requires an API token (`Authorization: Token <key>`). Anonymous requests get 401. Only the Swagger page and the schema stay public.
- Authenticated users can read. Create, update and delete require a staff user (403 otherwise).
- `POST /api/articles/by_url/predict/` and `POST /api/articles/by_url/fetch/` are staff-only and take `{"url": "..."}` in the body, because they create incidents, call paid model providers and fetch external pages. `fetch` accepts only public http(s) URLs.

## Lists, Pagination and Ordering

- All list endpoints (including `sources/by_url/articles` and `sources/by_url/media_incidents`) return `{count, next, previous, results}`.
- Use `limit` and `offset`. The default page size is 50 and `limit` is capped at 100. An invalid `limit` falls back to the default.
- `order_by` accepts one allow-listed field, optionally prefixed with `-`; any other value returns 400:
  - articles: `create_date`, `publication_date`, `title`
  - sources: `url`, `is_active`
  - media incidents: `create_date`, `update_date`, `status`
- Unexpected server errors return 500 with a generic message; details are only in server logs.

## Operational Notes

- Swagger UI is available for interactive contract exploration.
- API behavior should remain aligned with admin workflows and domain statuses.

## Change Guidance

When adding or changing endpoints:

1. Update serializer and viewset behavior together.
2. Add tests for list/detail behavior and filtering.
3. Update docs if response shape or semantics change.

## See Also

- Domain model: [DOMAIN.md](DOMAIN.md)
- Conventions: [CONVENTIONS.md](CONVENTIONS.md)
