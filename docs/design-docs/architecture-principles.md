# Architecture Principles

## Separation of Concerns

- Keep ingestion, parsing, prediction, and notification as distinct responsibilities.
- Keep web request handling separate from asynchronous batch workloads.

## Stable Domain Core

- Keep entity definitions and lifecycle semantics explicit.
- Prefer additive changes over implicit behavior coupling.

## Explicit Boundaries

- Integrations (Telegram, model providers, external sources) should be boundary concerns.
- Core logic should remain provider-agnostic where practical.

## Operational Predictability

- Scheduled chains should be observable and reproducible.
- Retries and failure behavior should be explicit for task reliability.

## Agent-Friendly Maintainability

- Favor clear module roles and deterministic flows.
- Keep docs aligned with architecture and linked from AGENTS.
