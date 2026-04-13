#!/usr/bin/env bash
set -e

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required"
  exit 1
fi

# Получаем PR для текущей ветки
PR_NUMBER=$(gh pr view --json number --template '{{.number}}')

if [ -z "$PR_NUMBER" ]; then
  echo "No PR found for current branch"
  exit 1
fi

echo "PR #$PR_NUMBER"
echo

# Получаем комментарии ревью
gh api repos/{owner}/{repo}/pulls/$PR_NUMBER/comments \
  --template '
{{range .}}
FILE: {{.path}}
LINE: {{.line}}
AUTHOR: {{.user.login}}

{{.body}}

----
{{end}}
'