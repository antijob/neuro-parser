# Development Workflow

This workflow is optimized for small, verifiable increments.

## Standard Loop

1. Read AGENTS and only the domain docs needed for the task.
2. Implement the feature or fix end-to-end.
3. Run full verification after implementation is complete.
4. Update docs when behavior, architecture, or operations changed.
5. Propose a focused PR summary with risk notes.

## Commands

- Install dependencies: `pdm install`
- Run tests: `pdm run pytest -v`
- Run lint: `pdm run flake8`
- Full check: `bash scripts/verify.sh`
- Docs integrity: `bash scripts/check-docs.sh`

## Scope Discipline

- Prefer narrow, reversible changes.
- Avoid touching unrelated modules.
- Keep asynchronous pipeline behavior observable and testable.

## When to Update Docs

Update docs for:

- Architecture or dependency direction changes
- Domain model or status lifecycle changes
- API contract changes
- Bot command or interaction changes
- ML pipeline or predictor behavior changes

## See Also

- Repository map: [repository-map.md](repository-map.md)
- Documentation maintenance: [documentation-maintenance.md](documentation-maintenance.md)
