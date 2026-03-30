# Tech Debt Tracker

Track debt that affects reliability, maintainability, or delivery speed.

## Open Items

### [P3] Pre-existing flake8 violations in server/
- **Scope:** `server/` (application source only; `.venv` is now excluded via setup.cfg)
- **Impact:** Developer throughput — lint step in `verify.sh` currently fails; does not block tests or docs checks
- **Counts (as of 2026-03-30):** E501 ×365, F401 ×51, W293 ×18, W292 ×7, F541 ×5, E302 ×6, F811 ×3, W291 ×3, others ×1–2
- **Suggested remediation:** Run `pdm run black server/ && pdm run isort server/` to fix formatting, then address unused imports manually
- **Status:** Open

### [P2] Tests require Rust toolchain (tokenizers)
- **Scope:** CI and local test runs
- **Impact:** `pdm install` fails without Rust compiler; `transformers` dependency pulls in `tokenizers` (Rust extension); tests are skipped in `verify.sh` without it
- **Suggested remediation:** Pin `tokenizers` to a Python-wheel-only version, or add Rust to the dev environment setup docs
- **Status:** Open

### [P3] Verification script mismatch (resolved)
- Previously used wrong project name, package manager, and paths — corrected 2026-03-30

### [P3] Generated DB schema doc is manual
- Documentation coverage for generated schema should be automated in future.

### [P3] Architecture layer dependency checks absent
- Consider stricter architecture checks for dependency direction between Django apps.

## Prioritization

- P1: Reliability or data-correctness risk
- P2: Developer throughput and maintainability impact
- P3: Cosmetic or low-frequency operational friction

## Entry Template

- Title
- Scope
- Impact
- Suggested remediation
- Priority
- Status
