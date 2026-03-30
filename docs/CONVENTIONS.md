# Conventions

## Python Style

- Formatter: black with line length 88
- Import sorting: isort (black profile)
- Linting: flake8 with bounded complexity
- Prefer explicit names and single-purpose functions in pipeline code

## Django Patterns

- Keep behavior grouped by application domain.
- Use split settings and environment-specific overrides.
- Keep model logic and orchestration concerns separate.

## Asynchronous Work

- Put long-running and scheduled operations in Celery tasks.
- Keep tasks idempotent where practical.
- Separate crawl, parse, and notify concerns to simplify retries.

## Testing

- Primary runner: pytest with Django integration
- Maintain strong coverage expectations for core flows
- Test business behavior, status transitions, and parsing edge cases

## Documentation

- Keep AGENTS minimal and stable.
- Put detailed rules in focused docs under progressive disclosure.
- Update docs whenever architecture, workflow, or public behavior changes.
