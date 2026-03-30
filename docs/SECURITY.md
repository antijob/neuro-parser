# Security

## Secrets and Credentials

- Keep all credentials in environment variables.
- Do not hardcode tokens in source or documentation.
- Rotate Telegram and model-provider tokens on compromise or role changes.

## Runtime Security

- Use Django security settings for host, CSRF, and middleware protections.
- Keep production and development settings clearly separated.
- Restrict access to administrative endpoints.

## Data Security

- Protect database credentials and backup artifacts.
- Limit data access by operational role.
- Review logs for accidental secret leakage.

## Dependency and Supply Chain

- Keep dependencies pinned and updated through planned maintenance.
- Run verification scripts before merges.
- Prefer transparent, well-understood dependencies.

## Incident Response

When a secret leak is suspected:

1. Revoke and rotate affected keys.
2. Audit recent logs and configuration changes.
3. Re-run verification and smoke checks.
4. Document follow-up remediation steps.

## See Also

- Conventions: [CONVENTIONS.md](CONVENTIONS.md)
- Agent workflow: [agents/development-workflow.md](agents/development-workflow.md)
