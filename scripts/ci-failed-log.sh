#!/usr/bin/env bash
set -euo pipefail

main() {
local RUN_ID=""
local WORKFLOW=""
local BRANCH=""
local LIMIT="20"
local RAW_LOG="false"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/ci-failed-log.sh [options]

Options:
  --run-id <id>         Show logs for a specific workflow run.
  --workflow <name>     Filter runs by workflow name/file (e.g. "verify" or "verify.yml").
  --branch <branch>     Filter runs by branch.
  --limit <n>           Number of recent runs to inspect (default: 20).
  --raw                 Print full failed log without grep filtering.
  -h, --help            Show this help.

Examples:
  bash scripts/ci-failed-log.sh
  bash scripts/ci-failed-log.sh --workflow verify --branch stage
  bash scripts/ci-failed-log.sh --run-id 123456789 --raw
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-id)
      RUN_ID="${2:-}"
      shift 2
      ;;
    --workflow)
      WORKFLOW="${2:-}"
      shift 2
      ;;
    --branch)
      BRANCH="${2:-}"
      shift 2
      ;;
    --limit)
      LIMIT="${2:-}"
      shift 2
      ;;
    --raw)
      RAW_LOG="true"
      shift
      ;;
    -h|--help)
      usage
      return 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      return 1
      ;;
  esac
done

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required." >&2
  return 1
fi

if [[ -z "$BRANCH" ]]; then
  BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
fi

if [[ -z "$RUN_ID" ]]; then
  list_args=(run list --limit "$LIMIT" --json databaseId,conclusion)

  if [[ -n "$WORKFLOW" ]]; then
    list_args+=(--workflow "$WORKFLOW")
  fi

  if [[ -n "$BRANCH" ]]; then
    list_args+=(--branch "$BRANCH")
  fi

  RUN_ID="$(gh "${list_args[@]}" --jq '[.[] | select(.conclusion=="failure")] | .[0].databaseId | tostring // ""')"

  if [[ -z "$RUN_ID" || "$RUN_ID" == "null" ]]; then
    echo "CI is passing — no failed runs found for branch '${BRANCH}'."
    return 0
  fi
fi

if [[ -z "$RUN_ID" ]]; then
  echo "No failed CI runs found with current filters." >&2
  return 1
fi

echo "=== CI failed log ==="
gh run view "$RUN_ID" \
  --json databaseId,workflowName,displayTitle,headBranch,event,status,conclusion,url \
  --jq '"Run #" + (.databaseId|tostring) + "\nWorkflow: " + .workflowName + "\nTitle: " + .displayTitle + "\nBranch: " + .headBranch + "\nEvent: " + .event + "\nStatus: " + .status + " / " + .conclusion + "\nURL: " + .url'
echo ""

LOG="$(gh run view "$RUN_ID" --log-failed 2>/dev/null || gh run view "$RUN_ID" --log)"

if [[ "$RAW_LOG" == "true" ]]; then
  echo "$LOG"
  return 0
fi

PATTERN='error|Error|ERROR|FAILED|failed|Traceback|AssertionError|TypeError|ReferenceError|ELIFECYCLE|Process completed with exit code|panic:|fatal'

echo "$LOG" | grep -Ein "$PATTERN" || {
  echo "No obvious error lines matched. Showing last 120 lines for context:"
  echo ""
  echo "$LOG" | tail -n 120
}
}

main "$@"