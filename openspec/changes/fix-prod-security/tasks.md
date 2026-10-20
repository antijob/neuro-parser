# Tasks

## 1. Production settings

- [x] 1.1 In `server/settings/environments/production.py`:
  - read `DEBUG` with `decouple` `cast=bool, default=False`;
  - read `ALLOWED_HOSTS` with `Csv()`, defaulting to `HOST` (reuse the existing `c` config object, design D1);
  - add a test under a `tests/` directory that loads production settings with `DEBUG=False` and asserts `settings.DEBUG is False` and that `ALLOWED_HOSTS` equals the `HOST` value.
  - Verify: `pdm run pytest -k settings` passes.
- [x] 1.2 Add a commented `ALLOWED_HOSTS` line with an explanation to `.env.template` (variable name only). Verify: `git diff .env.template` shows only that addition.
- [x] 1.3 Update `docs/SECURITY.md` (Runtime Security) to state that `DEBUG` is strictly boolean and hosts come from `ALLOWED_HOSTS`/`HOST`. Verify: `bash scripts/check-docs.sh` passes.

## 2. Docker build context

- [x] 2.1 Add `.telethon/`, `certs/`, `tmp/`, `*.session`, `celerybeat-schedule`, `app.log` and `.git/` to `.dockerignore` (design D7).
  - Verify: `NEURO_PARSER_VERSION=local docker compose -f docker-compose.prod.yaml build web`, then `docker run --rm antijob/neuro-parser:local ls -la /code/.telethon /code/certs` reports that both paths are missing.
- [x] 2.2 Add a short note to the Secrets section of `docs/SECURITY.md`: images must never contain the session or certificates; build from a clean checkout. Verify: `bash scripts/check-docs.sh` passes.

## 3. API access control

- [x] 3.1 Change `IsAdminOrReadOnly` in `server/apps/api/permissions.py`: safe methods require an authenticated user, all other methods require staff (design D2). Set it on `ArticleViewSet`.
  - Add `anon_client` and `staff_client` fixtures to `server/apps/api/tests/conftest.py`, reusing `staff_user`.
  - Add tests: anonymous GET on each of the four resources returns 401, non-staff DELETE/PATCH on articles and sources returns 403, staff PATCH returns 200.
  - Update the existing write tests in `test_article_view.py` and `test_source_view.py` to use `staff_client`.
  - Verify: `pdm run pytest server/apps/api -v` passes.
- [x] 3.2 Make `predict` and `fetch` in `server/apps/api/views/article_views.py` POST-only with `permission_classes=[IsAdminUser]`, reading `url` from the request body.
  - Tests: GET returns 405; non-staff POST returns 403; staff POST on `predict` calls `IncidentPredictor.predict` (mocked with `unittest.mock`).
  - Verify: `pdm run pytest server/apps/api -v` passes.
- [x] 3.3 Add `validate_public_http_url` in `server/apps/api/validators.py` (design D5) and call it in `fetch` before `get_or_create`.
  - Unit tests with `socket.getaddrinfo` mocked: http/https public address accepted; `file://`, `ftp://`, `127.0.0.1`, `10.0.0.1`, `169.254.169.254`, `::1` rejected.
  - API test: a rejected URL returns 400 and creates no `Article`.
  - Verify: `pdm run pytest server/apps/api -v` passes.

## 4. API lists, ordering and errors

- [x] 4.1 Add a `LimitOffsetPagination` subclass (`default_limit=50`, `max_limit=100`) and a `StrictOrderingFilter` (`OrderingFilter` with `ordering_param = "order_by"`, raising `ValidationError` on fields not in `ordering_fields`) in `server/apps/api/`. Register both in `REST_FRAMEWORK` in `server/settings/components/api.py` (design D3).
  - Unit test: `StrictOrderingFilter` rejects `assigned_to__password` and accepts `-create_date` for a view with that allow-list.
  - Verify: `pdm run pytest server/apps/api -v` passes.
- [x] 4.2 Declare `ordering_fields` per the spec allow-list on the article, source and media incident viewsets.
  - Replace the hand-written `order_by`/`limit` parsing in `ArticleViewSet.list`, `SourceViewSet.list`, `articles_by_url` and `media_incidents` with `filter_queryset`, `paginate_queryset` and `get_paginated_response`.
  - Tests: the list response has `count`/`next`/`previous`/`results`; `limit=1000` returns at most 100 items; `order_by=assigned_to__password` returns 400 on `sources/by_url/media_incidents`; `order_by=-publication_date` orders articles.
  - Verify: `pdm run pytest server/apps/api -v` passes.
- [x] 4.3 Remove the `except Exception as e: return Response({"error": str(e)})` blocks in `server/apps/api/views/`, keeping explicit 400 (missing `url`) and 404 (`DoesNotExist`) branches.
  - Extend `custom_exception_handler` to log unhandled exceptions and return a generic 500 JSON body (design D4).
  - Test: a view forced to raise `RuntimeError("secret detail")` returns 500 without `secret detail` in the body.
  - Verify: `pdm run pytest server/apps/api -v` passes.
- [x] 4.4 Update `docs/API.md`: token required for all endpoints except Swagger, staff-only writes, pagination shape and limits, the `order_by` allow-list, POST-only `predict`/`fetch`.
  - Update the REST API sections of `docs/ru/developers.md` and `docs/en/developers.md` as a pair.
  - Verify: `bash scripts/check-docs.sh` passes.

## 5. CI trust boundary

- [x] 5.1 Switch `check-docs.yml`, `verify.yml` and `tests.web.yml` to `runs-on: ubuntu-latest` (fall back to `ubuntu-22.04` if Python 3.9 is unavailable).
  - In `tests.web.yml`, mark the PR comment steps `continue-on-error: true`.
  - Verify: `actionlint` (or `gh workflow view`) reports no syntax errors.
- [x] 5.2 In `ci.yml` (design D6):
  - add `if: github.event_name != 'pull_request'` to `clean`, `build` and `start_prod`;
  - make `test` depend on `check-docs` and `verify` instead of `build`;
  - make `start_prod` depend on `build` and `test`;
  - drop `secrets: inherit` from `test`.
  - Verify: a draft PR runs only GitHub-hosted jobs, with `clean`/`build`/`start_prod` shown as skipped.
- [x] 5.3 Document the manual GitHub settings in `docs/SECURITY.md` under a new "CI and Runners" section: outside-collaborator approval, production runner group restricted to `ci.yml` on `main`/`stage`, `Prod` environment limited to `main`. Verify: `bash scripts/check-docs.sh` passes.

## 6. Release and verification

- [x] 6.1 Run `bash scripts/verify.sh` and check the output, not only the exit code: no new flake8 errors in changed files, and tests actually ran (not skipped).
- [ ] 6.2 Hand-off checklist for the maintainer, recorded in the PR description:
  - GitHub Variables `DEBUG`/`HOST` are correct;
  - manual GitHub settings from 5.3 are applied;
  - published Docker Hub tags are checked for `/code/.telethon` contents;
  - secret rotation is decided (design Risks);
  - after deploy: the 404 page has no URL list, anonymous `/api/sources/` returns 401, a staff token lists paginated sources.
