# Security

## Secrets and Credentials

- Keep all credentials in environment variables.
- Do not hardcode tokens in source or documentation.
- Rotate Telegram and model-provider tokens on compromise or role changes.
- Images must never contain the Telegram session (`.telethon/`), certificates (`certs/`) or `.env` files; `.dockerignore` enforces this, and images are built from a clean checkout.

## Runtime Security

- Use Django security settings for host, CSRF, and middleware protections.
- Keep production and development settings clearly separated.
- `DEBUG` is parsed as a strict boolean and is off unless set to a true value.
- Accepted hosts come from `ALLOWED_HOSTS`, which defaults to `HOST`.
- Restrict access to administrative endpoints.

## Data Security

- Protect database credentials and backup artifacts.
- Limit data access by operational role.
- Review logs for accidental secret leakage.

## Dependency and Supply Chain

- Keep dependencies pinned and updated through planned maintenance.
- Run verification scripts before merges.
- Prefer transparent, well-understood dependencies.

## CI and Runners

- Pull request CI (docs check, verify, tests) runs only on GitHub-hosted runners. Pull request code is untrusted.
- The production self-hosted runner runs only `clean`, `build` and `start_prod` for pushes to `main` and `stage` (or a manual dispatch by a maintainer).
- `ci.yml` skips those jobs for `pull_request` events with `if: github.event_name != 'pull_request'`; keep that condition on any new job that targets the production runner.

Settings that GitHub enforces, to be applied by a repository admin:

1. Settings > Actions > General > Fork pull request workflows: require approval for all outside collaborators.
2. Settings > Actions > Runner groups: restrict the group with the production runner to the `ci.yml` workflow on the `main` and `stage` branches.
3. Settings > Environments > `Prod`: limit deployment branches to `main`.

## Incident Response

When a secret leak is suspected:

1. Revoke and rotate affected keys.
2. Audit recent logs and configuration changes.
3. Re-run verification and smoke checks.
4. Document follow-up remediation steps.

## See Also

- Conventions: [CONVENTIONS.md](CONVENTIONS.md)
- Agent workflow: [agents/development-workflow.md](agents/development-workflow.md)
