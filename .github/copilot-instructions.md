---
description: Standard workflow when implementing features
alwaysApply: true
---

# Feature Development Workflow

Read [AGENTS.md](../AGENTS.md) first. Use it as a short map and follow links to deeper docs only when needed.

Primary workflow reference: [docs/agents/development-workflow.md](../docs/agents/development-workflow.md)

When asked to implement a feature:

1. **Implement** — make all necessary code changes for the task
2. **Complete implementation** — ensure all parts of the feature are finished
3. **Verify** — run `./scripts/verify.sh` ONLY after completing all implementation work
4. **Fix** — if verify fails, fix issues and re-run
5. **Update docs** — update documentation if architecture/API changed
6. **Propose PR** — suggest: branch name, conventional commit message, summary of changes

**Important**: Do not run verification or documentation updates during intermediate steps - only after the complete task is finished.

Before proposing a PR, ensure:

- [ ] Verify passed successfully
- [ ] Documentation updated (if architecture/API changed)
- [ ] `bash scripts/check-docs.sh` run (if docs were modified)
