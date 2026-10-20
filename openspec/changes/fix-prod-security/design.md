# Design: fix-prod-security

## Context

See proposal.md for motivation. Current state that shapes the approach:

- **Production settings.** `server/settings/environments/production.py` reads `DEBUG` with `decouple.config` and no `cast`, so any non-empty string is truthy. It sets `ALLOWED_HOSTS = ["*"]`. Deploy (`.github/workflows/deploy.yml`) already writes `HOST` and optionally `DEBUG` into `.env`.
- **CI.**
  - `ci.yml` runs on `pull_request` and on pushes to `main`/`stage`.
  - Every job (`check-docs`, `verify`, `clean`, `build`, `test`, `start_prod`) targets `[self-hosted, neuroparser, production]`.
  - `build` runs `docker compose -f docker-compose.prod.yaml build web` on the production host for PRs too. It pushes to the registry only for `main`/`stage` or a forced build.
  - `tests.web.yml` builds its own image through the dev compose file (`--build`), so it does not use the image from `build`.
- **Docker build context.** The web Dockerfile does `ADD . /code/`. `.dockerignore` excludes `.env*` and `models` but not `.telethon/` or `certs/`. In production `.telethon` is a named volume (`thelethon:/code/.telethon`), so the image does not need it.
- **API.**
  - Global DRF settings already require `TokenAuthentication` and `IsAuthenticated`.
  - `IsAdminOrReadOnly` (`server/apps/api/permissions.py`) returns True for safe methods without checking authentication, which overrides the global default on the incident type, media incident and source viewsets.
  - `ArticleViewSet` has no `permission_classes`, so any authenticated user can write.
  - List methods and `by_url/*` actions implement `order_by` and `limit` by hand, pass `order_by` straight to `QuerySet.order_by`, and return `str(e)` from broad `except` blocks.
  - No pagination class is configured.

## Goals / Non-Goals

**Goals:**

- Close the four exposures with the smallest code surface, using DRF and decouple features that already ship with the pinned versions.
- Leave production deploy behavior for `main` unchanged apart from where jobs run.

**Non-Goals:**

- Splitting the API into versions or adding new token types.
- Reworking the web image build or compose topology (tracked in #351).
- Fixing the `fetch` action's call into the fetcher.

## Decisions

### D1. decouple casts for settings

- `DEBUG = c("DEBUG", default=False, cast=bool)`. decouple's bool cast maps `""`, `0`, `false`, `no`, `off` to False.
- `ALLOWED_HOSTS = c("ALLOWED_HOSTS", default=c("HOST", default=""), cast=Csv())`.
- **Alternative considered:** hardcoding the domain. Rejected, because stage and production use different `HOST` values that deploy already provides.

### D2. Permission class semantics

- Change `IsAdminOrReadOnly` so that safe methods require `request.user.is_authenticated` and other methods require `is_staff`. Apply it to `ArticleViewSet` as well.
- Keep the class name to avoid churn in four viewsets.
- **Alternative considered:** a new `IsStaffOrAuthenticatedReadOnly` class. Rejected as a parallel implementation of the same rule.
- The `predict` and `fetch` actions declare `permission_classes=[IsAdminUser]` (DRF built-in) and `methods=["post"]`.

### D3. Pagination and ordering through DRF, not hand-written code

- **Pagination:** set `DEFAULT_PAGINATION_CLASS` to a subclass of DRF `LimitOffsetPagination` with `default_limit=50` and `max_limit=100`.
  - `LimitOffsetPagination` already uses the `limit` parameter name that clients pass today.
  - It already falls back to the default when `limit` is invalid.
- **Ordering:** add a `StrictOrderingFilter` subclass of DRF `OrderingFilter` with `ordering_param = "order_by"`.
  - It raises `ValidationError` (400) on any field outside the view's `ordering_fields`, instead of dropping it silently.
  - Each viewset declares `ordering_fields` from the spec allow-list.
- **Custom list actions** (`sources/by_url/articles`, `sources/by_url/media_incidents`) and overridden `list` methods call `self.filter_queryset(...)`, `self.paginate_queryset(...)` and `self.get_paginated_response(...)`. That removes the duplicated `order_by`/`limit` parsing in `article_views.py` and `source_views.py`.
- **Alternative considered:** a hand-written allow-list check inside each view. Rejected, because it repeats the same logic in five places.

### D4. Errors go through the existing exception handler

- Remove the `except Exception as e: return Response({"error": str(e)})` blocks.
  - Expected cases stay explicit: missing `url` gives 400, `DoesNotExist` gives 404.
  - Everything else propagates.
- Extend `custom_exception_handler` (`server/apps/api/exception_handler.py`): when DRF returns `None` (an unhandled exception), log it with `logger.exception` and return `{"error": "Internal server error", "status_code": 500}`.
  - The handler already adds `status_code` for handled errors, so the response shape stays consistent.

### D5. URL validation for fetch

- A new helper `validate_public_http_url(url)` in `server/apps/api/validators.py`:
  - parses with `urllib.parse`;
  - requires an `http`/`https` scheme and a host;
  - resolves the host with `socket.getaddrinfo`;
  - rejects the URL if any resolved address is private, loopback, link-local, reserved, multicast or unspecified (`ipaddress` properties).
- The `fetch` action calls it before `get_or_create`, so rejected URLs leave no rows.
- **Limitation:** this does not prevent DNS rebinding between validation and fetch. That is acceptable while the endpoint is staff-only and functionally broken (see Out of Scope in the proposal).

### D6. CI split by trust level

- `check-docs.yml`, `verify.yml` and `tests.web.yml` switch to `runs-on: ubuntu-latest`. They are self-contained:
  - verify installs dependencies with PDM;
  - tests start the dev compose stack with their own Postgres and Redis.
- In `ci.yml`:
  - `clean`, `build` and `start_prod` get `if: github.event_name != 'pull_request'`.
  - `test` no longer `needs: build`; it needs `check-docs` and `verify`.
  - `start_prod` needs both `build` and `test`.
- `secrets: inherit` is removed from `test`; the tests use only stub values.
- **Manual GitHub settings** (documented in tasks, applied by a maintainer):
  - Actions: require approval for outside collaborators.
  - Restrict the production runner group to `ci.yml` on `main`/`stage`.
  - Restrict the `Prod` environment's deployment branches to `main`.
- **Alternative considered:** a second self-hosted runner on a separate VM. Rejected for now: GitHub-hosted runners are free for public repositories and are ephemeral by design.

### D7. .dockerignore

- Add `.telethon/`, `certs/`, `tmp/`, `*.session`, `celerybeat-schedule`, `app.log` and `.git/`.
- Nothing in the Dockerfile copies these paths explicitly, so builds are unaffected.

## Reuse

| Need | Reused | New |
|---|---|---|
| Boolean and list env parsing | `decouple` `cast=bool`, `Csv` | none |
| Auth and read/write split | DRF `TokenAuthentication`, existing `IsAdminOrReadOnly`, DRF `IsAdminUser` | none |
| Pagination | DRF `LimitOffsetPagination` | a subclass setting the limits |
| Ordering allow-list | DRF `OrderingFilter`, `GenericAPIView.filter_queryset` | `StrictOrderingFilter` (about 10 lines), because the built-in filter drops invalid fields silently instead of returning 400 |
| Error responses | existing `custom_exception_handler` | fallback branch for unhandled errors |
| URL safety | stdlib `urllib.parse`, `ipaddress`, `socket` | `validate_public_http_url`; no URL-safety helper exists in `server/libs` or `server/core` |
| Test fixtures | `server/apps/api/tests/conftest.py` (`staff_user`, `regular_user`, `api_client`, `source`, `article`) | `staff_client` and `anon_client` fixtures next to `api_client` |

## Environment Variables

- `ALLOWED_HOSTS` (optional, comma-separated; defaults to `HOST`).
- `DEBUG` (existing; semantics now strictly boolean).

## Risks / Trade-offs

- **[Risk]** A `Host` header that is not in `ALLOWED_HOSTS` (an IP, or `localhost` inside the container) now gets 400.
  - **Mitigation:** no internal HTTP calls to `web` were found. After deploy, check Flower, static files and the admin through `HOST`. If something breaks, add hosts with `ALLOWED_HOSTS`.
- **[Risk]** Paginated responses and POST-only actions break any undocumented client.
  - **Mitigation:** the user confirmed there are no external clients. Swagger reflects the new contract.
- **[Risk]** Python 3.9 availability on GitHub-hosted `ubuntu-latest` for `verify.yml`.
  - **Mitigation:** pin `runs-on: ubuntu-22.04` if `setup-python` cannot provide 3.9 on the latest image.
- **[Risk]** PR comment actions in `tests.web.yml` cannot write to PRs from forks (read-only token).
  - **Mitigation:** mark those reporting steps `continue-on-error: true`. The job summary still holds the report.
- **[Risk]** Production has been running with debug pages on, so tracebacks may have exposed local variables.
  - **Mitigation:** an operational follow-up to review access logs for error pages and rotate the Telegram bot token, the Replicate token and the Django `SECRET_KEY` if exposure is suspected.
- **[Risk]** Earlier images on Docker Hub may already contain `.telethon` sessions.
  - **Mitigation:** inspect the published tags. If a session is found, terminate it in Telegram and re-create it with `init_telethon_client`.

## Migration Plan

1. Merge to `main`. The first PR that carries these workflow changes already runs on GitHub-hosted runners.
2. Before the deploy job runs, check that GitHub Variables `DEBUG` (unset or `False`) and `HOST` are correct.
3. After deploy:
   - a 404 page shows no URL list;
   - an anonymous request to `/api/sources/` returns 401;
   - a staff token can still list and paginate.
4. Apply the manual GitHub settings from D6.
5. **Rollback:** revert the merge commit and redeploy. There are no database migrations, so rollback is safe at any point.
