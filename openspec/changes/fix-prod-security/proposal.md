# Proposal: fix-prod-security

## Why

A repository audit found four exposures that affect the production system right now and are cheap to close compared with their impact:

- Production runs with Django debug mode effectively enabled.
- Pull request code runs on the production host.
- Local image builds can bake a Telegram account session and a TLS private key into a pushed image.
- The REST API lets anonymous clients read all data and order results by arbitrary model paths, including user password hashes.

These need to be fixed before the reliability work tracked in the issue tracker.

## What Changes

- **Production settings**
  - `DEBUG` is parsed as a boolean and defaults to off.
  - `ALLOWED_HOSTS` is taken from the environment (defaulting to `HOST`) instead of `*`.
- **CI trust boundary**
  - Pull request jobs (docs check, verify, tests) run on GitHub-hosted runners.
  - The production self-hosted runner only runs image build, cleanup and deploy for pushes to `main` and `stage`.
  - Repository and runner settings that GitHub enforces are documented as manual steps.
- **Docker build context**
  - `.dockerignore` excludes `.telethon/`, `certs/` and local runtime artifacts, so the image never contains the Telegram session or TLS keys.
- **REST API hardening**
  - **BREAKING**: every API endpoint except the schema/Swagger page requires token authentication. Anonymous requests get 401.
  - Write operations on all API resources (create, update, delete) require a staff user. Today any authenticated user can modify or delete articles.
  - **BREAKING**: list endpoints, including custom `by_url/...` lists, return paginated responses (`count`, `next`, `previous`, `results`) using `limit`/`offset` with a bounded maximum.
  - `order_by` accepts only an allow-listed set of fields per resource; anything else returns 400.
  - Error responses no longer echo internal exception text.
  - **BREAKING**: `articles/by_url/predict` and `articles/by_url/fetch` become POST-only and staff-only, because they trigger paid model calls, create incidents and fetch external URLs.
  - `fetch` rejects URLs that are not http(s) or that resolve to private, loopback or link-local addresses.

## Capabilities

### New Capabilities

- `api-access`: authentication, authorization, pagination, ordering and side-effect rules of the REST API.
- `deployment-security`: production runtime configuration, image contents, and the CI boundary between untrusted code and production infrastructure.

### Modified Capabilities

None. The existing specs (`telegram-subscriptions`, `incident-review`, `pipeline-operations`) describe bot, admin and pipeline behavior, and this change does not touch it.

## Impact

- **Domains:** api, settings, CI/CD, Docker build. Celery, ML, bot and admin behavior are unchanged.
- **Code:**
  - `server/settings/environments/production.py`, `server/settings/components/api.py`, `.env.template`
  - `server/apps/api/` (permissions, views, a new pagination/ordering helper)
  - `.dockerignore`
  - `.github/workflows/ci.yml`, `check-docs.yml`, `verify.yml`, `tests.web.yml`
- **Existing tests:** API tests that write as a regular user change expectations, because writes become staff-only.
- **Operations:**
  - GitHub Variables `DEBUG` and `HOST` must be correct before deploy.
  - GitHub repository, runner group and environment settings are changed manually.
  - Already published images on Docker Hub must be checked for leaked session files.
- **API consumers:** no external clients are known; the breaking changes are accepted.

## Out of Scope

- Fixing the functional bug in `articles/by_url/fetch` (it calls the fetcher without a source). This change only locks the endpoint down.
- Moving MediaIncident visibility to `PUBLIC_STATUSES`; all reads require a token instead.
- Dependency upgrades, Sentry and logging configuration, and reliability fixes. These are tracked in issues #342 to #352.
- Rotating secrets that may have been exposed through debug pages. This is flagged as an operational follow-up in design.
