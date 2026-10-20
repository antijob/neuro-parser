# Spec Delta

## Purpose

Defines security guarantees of the production deployment: runtime configuration, built image contents, and isolation of untrusted CI code from production infrastructure.

## ADDED Requirements

### Requirement: Debug output disabled in production

The production configuration SHALL run with debug mode off unless `DEBUG` is explicitly set to a true boolean value. Values such as `False`, `0`, an empty string or a missing variable SHALL keep debug mode off.

#### Scenario: Template value keeps debug off

- **WHEN** production settings load with `DEBUG=False` from the environment
- **THEN** debug mode is off and error pages show no tracebacks, settings or URL patterns

#### Scenario: Unknown URL in production

- **WHEN** a visitor requests a URL that does not exist
- **THEN** the response is a plain 404 page that does not list the project's URL patterns

### Requirement: Host header validation

The production configuration SHALL accept requests only for host names listed in `ALLOWED_HOSTS` from the environment, defaulting to the deployment `HOST`.

#### Scenario: Unknown host is rejected

- **WHEN** a request reaches the web application with a `Host` header that is not allowed
- **THEN** the application responds with 400

### Requirement: Secrets excluded from images

Application images SHALL NOT contain the Telegram client session directory, TLS certificates or keys, or environment files, regardless of what exists in the local working tree at build time.

#### Scenario: Local build with secrets present

- **WHEN** a developer builds the web image from a working tree that contains `.telethon/` session files and `certs/`
- **THEN** the built image contains neither the session files nor the certificate files

### Requirement: Untrusted code never runs on production infrastructure

CI jobs triggered by pull requests SHALL run only on isolated, ephemeral runners. The production self-hosted runner SHALL run only jobs for pushes to protected branches (`main`, `stage`) or manual dispatch by maintainers.

#### Scenario: Pull request CI

- **WHEN** a pull request is opened or updated
- **THEN** docs checks, verification and tests run on GitHub-hosted runners, and no job is scheduled on the production runner

#### Scenario: Push to main

- **WHEN** a commit is pushed to `main`
- **THEN** checks and tests run, and image build and deploy run on the production runner only after they pass
