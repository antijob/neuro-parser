# Spec Delta

## Purpose

Defines who can call the REST API, what they may change, and how list results, ordering, errors and side-effecting actions behave.

## ADDED Requirements

### Requirement: Token authentication

Every REST API endpoint SHALL require a valid API token, except the API schema and Swagger documentation pages.

#### Scenario: Anonymous request is rejected

- **WHEN** a client calls any resource endpoint under `/api/` without a token
- **THEN** the API responds with 401 and returns no resource data

#### Scenario: Documentation stays public

- **WHEN** a client opens the Swagger page or the API schema without a token
- **THEN** the page is returned with 200

### Requirement: Staff-only writes

The API SHALL allow create, update and delete operations on incident types, media incidents, sources and articles only to staff users. Authenticated non-staff users SHALL have read-only access.

#### Scenario: Regular user cannot delete an article

- **WHEN** an authenticated non-staff user sends DELETE to `/api/articles/by_url/`
- **THEN** the API responds with 403 and the article still exists

#### Scenario: Staff user updates a source

- **WHEN** a staff user sends PATCH to `/api/sources/by_url/` with valid fields
- **THEN** the API responds with 200 and the source is updated

### Requirement: Paginated lists

Every endpoint that returns a list SHALL return a paginated object with `count`, `next`, `previous` and `results`, controlled by `limit` and `offset` query parameters. The default page size SHALL be 50 and `limit` SHALL be capped at 100.

#### Scenario: Default page

- **WHEN** an authenticated client lists articles without `limit`
- **THEN** the response contains at most 50 items in `results` and the total in `count`

#### Scenario: Limit above the cap

- **WHEN** an authenticated client requests a list with `limit=1000`
- **THEN** the response contains at most 100 items in `results`

#### Scenario: Invalid limit

- **WHEN** an authenticated client passes a non-numeric `limit`
- **THEN** the API ignores it and returns the default page size

### Requirement: Allow-listed ordering

The `order_by` parameter SHALL accept only these fields, each optionally prefixed with `-` for descending order: for articles `create_date`, `publication_date`, `title`; for sources `url`, `is_active`; for media incidents `create_date`, `update_date`, `status`. Any other value SHALL be rejected.

#### Scenario: Allowed field

- **WHEN** an authenticated client lists articles with `order_by=-publication_date`
- **THEN** results are ordered by publication date, newest first

#### Scenario: Field outside the allow-list

- **WHEN** a client passes an `order_by` value that is not in the allow-list, including any related-field path such as `assigned_to__password`
- **THEN** the API responds with 400 and an error listing the allowed fields, and no query is ordered by that value

### Requirement: Error responses without internals

The API SHALL NOT include internal exception messages, stack traces or database errors in response bodies. Unexpected errors SHALL return 500 with a generic message, and the details SHALL be logged on the server.

#### Scenario: Unexpected error

- **WHEN** an unexpected exception occurs while handling a request
- **THEN** the client receives 500 with a generic error message and the exception is logged server-side

### Requirement: Side-effecting article actions

The article actions `by_url/predict` and `by_url/fetch` SHALL accept only POST requests from staff users, because they create incidents, call paid model providers and fetch external URLs.

#### Scenario: GET on predict

- **WHEN** any client sends GET to `/api/articles/by_url/predict/`
- **THEN** the API responds with 405 and no prediction runs

#### Scenario: Non-staff POST on predict

- **WHEN** an authenticated non-staff user sends POST to `/api/articles/by_url/predict/`
- **THEN** the API responds with 403 and no prediction runs

### Requirement: Safe URLs for fetch

The fetch action SHALL accept only `http` and `https` URLs whose host does not resolve to a private, loopback, link-local or reserved address.

#### Scenario: Internal address is rejected

- **WHEN** a staff user posts a fetch request for `http://127.0.0.1/` or a host resolving to a private network address
- **THEN** the API responds with 400 and no article is created or fetched

#### Scenario: Unsupported scheme is rejected

- **WHEN** a staff user posts a fetch request for a `file://` or `ftp://` URL
- **THEN** the API responds with 400 and no article is created or fetched
