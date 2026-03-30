# Documentation Maintenance

## Goal

Keep documentation as a reliable system of record for humans and agents.

## Rules

- Keep root AGENTS short and stable.
- Move detailed instructions into focused docs.
- Prefer capability descriptions over brittle path inventories.
- Link related docs so agents can progressively disclose context.

## Update Triggers

Update relevant docs whenever you change:

- architecture or service boundaries
- domain entities or lifecycle statuses
- API contracts
- bot interaction patterns
- ML predictors and decision logic
- security-critical behavior

## Review Checklist

1. Are all changed behaviors reflected in docs?
2. Are links valid and discoverable from AGENTS?
3. Is any instruction stale or contradictory?
4. Can a new contributor find the right doc in under one minute?

## Verification

- Run `bash scripts/check-docs.sh` after docs edits.
- Run `bash scripts/verify.sh` for full project checks.
