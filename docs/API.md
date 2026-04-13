# API

The API surface is built with Django REST Framework and exposes incident, source, and article data.

## API Scope

- Incident type listing and filtering
- Media incident retrieval for downstream consumers
- Source and article visibility for diagnostics and operations

## Design Notes

- Use serializers for stable payload contracts.
- Keep queryset filtering explicit and safe.
- Use predictable pagination and sorting behavior for list endpoints.

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
