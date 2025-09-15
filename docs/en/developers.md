# Developer Guide

This document contains instructions for developers, including Python package management, local and production project deployment, Telegram bot setup, message distribution, and API usage.

## Python Package Management

We use [PDM](https://pdm-project.org/) to manage Python packages:

```bash
# install all locked packages from the lock file
pdm install

# resolve all dependencies and lock packages in the lock file
pdm lock

# update all packages
pdm update

# add a new package to pyproject.toml without creating a venv
pdm add --no-sync <package_name>
```

`pyproject.toml` and `pdm.lock` files should be included in git.

---

## Local Deployment

1. Create a `.env` file based on `.env.template` and initialize the database.
2. Run the following command in the root directory to start the local container:

```bash
docker-compose up -d
```

3. Add the following lines to `/etc/hosts` to resolve local Traefik domains:

```bash
127.0.0.1 report.local
127.0.0.1 flower-report.local
```

4. Access the admin panel: `http://report.local/s/ecret/admin` or use the API: `http://report.local/api`.

5. To start full system operation, you need to add links to sources and incident types for tracking

---

## Production Deployment

1. Modify the `config/.env` file and create the database.
2. Run the following command in the root directory to start the production container:

```bash
docker-compose -f docker-compose.prod.yaml up -d
```

---

## Project diagram

See on [GitDiagram](https://gitdiagram.com/antijob/neuro-parser)

## Telegram Bot Setup

You can use the Telegram bot to receive notifications about new incidents.

### Configuration

1. Register a new bot through [BotFather](https://t.me/BotFather).
2. Add the following settings to the `.env` file:

```bash
TELEGRAM_BOT_TOKEN=
```

- `TELEGRAM_BOT_TOKEN` - Token issued by BotFather.

3. Create a new Telegram chat, add the bot, it will remember it and send notifications about new incidents.
4. To receive notifications only for specific categories, use the `/categ` command in the chat.
5. You can also manage channels through the Django admin panel in the Bot section.

---

## Model APIs

External models are called using [Replicate.com](https://replicate.com/), which is a more cost-effective alternative to ChatGPT.

---

## REST API Interface

Built on `django-rest-api-framework`, documentation is automatically generated via Swagger and available at the `/swagger-ui` path.

---

## Infrastructure

Two remote machines were created for `stage` and `prod` environments.
They are configured identically, with the server launching the same way as locally:

```bash
docker compose -f docker-compose.prod.yaml pull
docker-compose -f docker-compose.prod.yaml -d
```

A more detailed deployment process can be seen in [deploy.yml](.github/workflows/deploy.yml).

> [!NOTE] Note
> Working directory on servers where the server version is running: `/opt/services/neuro-parser`.
> Current information about the server launch location is in `$DEPLOY_LOCATION` in the [deploy.yml](.github/workflows/deploy.yml) file.

> [!WARNING] Important!
> The `github-actions` working directory (`/home/github-actions/_work/neuro-parser`) is used only for repository cloning.
> The project should not be launched or run in this directory.

### Typical Operations on Servers

- To diagnose errors in the environment (`stage` or `prod`), you can view container logs:

  ```bash
  # View logs for a specific container
  # web - server (admin panel), bot - Telegram bot, celery - queue tasks
  docker logs neuro-parser-web-1
  # or
  cd /opt/services/neuro-parser
  docker-compose -f docker-compose.prod.yml logs -f
  ```

- To execute and test scripts inside containers:
  
  ```bash
  # web - server (admin panel), bot - TG bot, celery - queue tasks
  docker exec -it neuro-parser-web-1 bash
  # or
  cd /opt/services/neuro-parser
  docker-compose -f docker-compose.prod.yml exec -it web bash
  ```

- **Ran out of space. Server reports `No space left on disk` error.**
  Most likely, space ran out due to constant building or downloading of images. They should be cleared periodically, but in rare cases, this may not be enough. You can try to manually clear space:

  ```bash
  docker container prune -f
  docker image prune -af
  # check disk space
  df -h
  ```

---

## Contributing

We welcome community participation. Please follow the instructions in the [CONTRIBUTING.md](https://github.com/antijob/neuro-parser/blob/main/CONTRIBUTING.md) file.

---

## Contacts

If you have questions or need assistance, contact us at <info@antijob.net>.
