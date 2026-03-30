#!/usr/bin/env bash
# check-docs.sh — Validate documentation structure and integrity
# Usage: bash scripts/check-docs.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

ERRORS=0

echo "=== neuro-parser — Documentation Check ==="
echo ""

# --- Required files ---
echo "--- Checking required files ---"
REQUIRED_FILES=(
    "AGENTS.md"
    "docs/ARCHITECTURE.md"
    "docs/DOMAIN.md"
    "docs/CONVENTIONS.md"
    "docs/API.md"
    "docs/BOT.md"
    "docs/ML.md"
    "docs/SECURITY.md"
    "docs/agents/development-workflow.md"
    "docs/agents/documentation-maintenance.md"
    "docs/agents/repository-map.md"
    "docs/design-docs/index.md"
    "docs/design-docs/core-beliefs.md"
    "docs/design-docs/architecture-principles.md"
    "docs/design-docs/doc-gardening.md"
    "docs/exec-plans/tech-debt-tracker.md"
    "docs/exec-plans/active/_template.md"
    "docs/product-specs/index.md"
    "docs/product-specs/user-flows.md"
    "docs/generated/db-schema.md"
    "docs/references/llm-references.md"
)

for f in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$f" ]]; then
        echo "  ✗ MISSING: $f"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✓ $f"
    fi
done
echo ""

# --- Required directories ---
echo "--- Checking required directories ---"
REQUIRED_DIRS=(
    "docs"
    "docs/agents"
    "docs/design-docs"
    "docs/exec-plans"
    "docs/exec-plans/active"
    "docs/product-specs"
    "docs/generated"
    "docs/references"
    "scripts"
)

for d in "${REQUIRED_DIRS[@]}"; do
    if [[ ! -d "$d" ]]; then
        echo "  ✗ MISSING DIR: $d"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✓ $d/"
    fi
done
echo ""

# --- Non-empty files ---
echo "--- Checking files are non-empty ---"
for f in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$f" && ! -s "$f" ]]; then
        echo "  ✗ EMPTY: $f"
        ERRORS=$((ERRORS + 1))
    fi
done
echo ""

# --- AGENTS.md references ---
echo "--- Checking AGENTS.md references ---"
AGENTS_REFS=(
    "docs/ARCHITECTURE.md"
    "docs/DOMAIN.md"
    "docs/CONVENTIONS.md"
    "docs/API.md"
    "docs/BOT.md"
    "docs/ML.md"
    "docs/SECURITY.md"
    "docs/agents/development-workflow.md"
    "docs/agents/documentation-maintenance.md"
    "docs/agents/repository-map.md"
)

for ref in "${AGENTS_REFS[@]}"; do
    if ! grep -q "$ref" AGENTS.md 2>/dev/null; then
        echo "  ✗ AGENTS.md missing reference to $ref"
        ERRORS=$((ERRORS + 1))
    else
        echo "  ✓ AGENTS.md -> $ref"
    fi
done
echo ""

# --- No stale project references ---
echo "--- Checking for stale project references ---"
STALE_TERMS=("Antijob Reviews Bot")
for term in "${STALE_TERMS[@]}"; do
    hits=$(grep -ril "$term" AGENTS.md docs/ 2>/dev/null || true)
    if [[ -n "$hits" ]]; then
        echo "  ✗ Found '$term' in: $hits"
        ERRORS=$((ERRORS + 1))
    fi
done
if [[ $ERRORS -eq 0 ]]; then
    echo "  ✓ No stale project references"
fi
echo ""

# --- Summary ---
if [[ $ERRORS -gt 0 ]]; then
    echo "=== FAILED: $ERRORS error(s) found ==="
    exit 1
else
    echo "=== All documentation checks passed ==="
    exit 0
fi
