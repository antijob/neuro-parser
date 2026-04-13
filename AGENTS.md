# AGENTS

neuro-parser is a Django-based news parsing and ML incident detection platform with Telegram bot integration.

## Essentials

- Package manager: PDM
- Python version: 3.9+
- Local stack: Docker Compose (web, postgres, redis, celery, flower, traefik)
- Test runner: pytest
- Lint and format: flake8, isort, black

## Common Commands

- Install dependencies: `pdm install`
- Run local stack: `docker-compose up -d`
- Run tests: `pdm run pytest -v`
- Run lint: `pdm run flake8`
- Full verification: `bash scripts/verify.sh`
- Documentation checks: `bash scripts/check-docs.sh`

## Project Map (Progressive Disclosure)

Start here, then read only what is needed for the current task:

- System architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- Domain concepts and lifecycle: [docs/DOMAIN.md](docs/DOMAIN.md)
- Coding and testing conventions: [docs/CONVENTIONS.md](docs/CONVENTIONS.md)
- REST API implementation guidance: [docs/API.md](docs/API.md)
- Telegram bot behavior and patterns: [docs/BOT.md](docs/BOT.md)
- ML prediction pipeline and models: [docs/ML.md](docs/ML.md)
- Security and secrets handling: [docs/SECURITY.md](docs/SECURITY.md)

## Agent Workflows

- Feature workflow for this repository: [docs/agents/development-workflow.md](docs/agents/development-workflow.md)
- Capability-oriented repository navigation: [docs/agents/repository-map.md](docs/agents/repository-map.md)
- Documentation maintenance rules: [docs/agents/documentation-maintenance.md](docs/agents/documentation-maintenance.md)

## Notes

- Prefer capability-based navigation over relying on hardcoded file paths.
- Keep root AGENTS short; place detailed guidance in docs and cross-link it.
