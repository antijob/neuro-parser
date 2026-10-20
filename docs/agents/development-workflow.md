# Development Workflow

This workflow is optimized for small, verifiable increments.

## Standard Loop

1. Read AGENTS and only the domain docs needed for the task.
2. If the task has an OpenSpec change in `openspec/changes/`, follow its `tasks.md`.
3. Implement the feature or fix end-to-end.
4. Run full verification after implementation is complete.
5. Update docs when behavior, architecture, or operations changed.
6. Propose a focused PR summary with risk notes.

## Spec-Driven Changes (OpenSpec)

OpenSpec commands are configured for Claude Code. Other agents do not create OpenSpec changes, but follow an existing change's `tasks.md` (Standard Loop, step 2).

For features and non-trivial changes, plan with OpenSpec before coding:

1. `/opsx:propose "<idea>"` creates `openspec/changes/<name>/` with proposal, design, specs and tasks.
2. `/opsx:apply` implements the tasks.
3. `/opsx:archive` merges delta specs into `openspec/specs/` and archives the change.

Discussion happens in Russian; stored artifacts are written in English (see `openspec/config.yaml`).

- Behavior specs (requirements and scenarios) live in `openspec/specs/`.
- Change plans live only in `openspec/changes/`; `docs/exec-plans/` keeps the tech debt tracker.
- Cross-cutting decisions from a change's `design.md` are promoted to `docs/design-docs/`.

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
