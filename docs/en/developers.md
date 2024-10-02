# Development Guide

This document provides guidelines for developers contributing to the project, covering Python package management, running the project locally or in production, setting up a Telegram bot, broadcasting messages, and API usage.

## Table of Contents
1. [Managing Python Packages](#managing-python-packages)
1. [Running Locally](#running-locally)
1. [Running in Production](#running-in-production)
1. [Telegram Bot Setup](#telegram-bot-setup)
1. [Model API](#model-api)
1. [REST API Interface](#rest-api-interface)
1. [Infrastructure](#infrastructure)
1. [Contributing](#contributing)
1. [Contact](#contact)

---

## Managing Python Packages

For managing Python packages, we use [PDM](https://pdm-project.org/):

```bash
# install all locked packages from lock file
pdm install

# resolve all dependencies and lock packages to lock file
pdm lock

# update all packages
pdm update

# add new package to pyproject.toml without creating venv
pdm add --no-sync <package_name>
```

Both `pyproject.toml` and `pdm.lock` files should be included in git.

---

## Running Locally

1. Create an `.env` file from `.env.template` and initialize the database.
2. Run the following command inside the root directory to start the local container:

```bash
docker-compose up -d
```

3. Add the following lines to your `/etc/hosts` file to resolve local domains for Traefik:

```bash
127.0.0.1 report.local
127.0.0.1 flower-report.local
```

4. Access the admin panel at `http://report.local/s/ecret/admin` or use the API at `http://report.local/api`.

5. For the system to work fully, add links to sources and incident types for tracking.

---

## Running in Production

1. Modify the `config/.env` file and create the database.
2. Run the following command inside the root directory to start the production container:

```bash
docker-compose -f docker-compose.prod.yaml up -d
```

---

## Telegram Bot Setup

You can use the Telegram bot to receive notifications about new incidents.

### Setup

1. Register a new bot with [BotFather](https://t.me/BotFather).
2. Add the following settings to the `.env` file:

```bash
TELEGRAM_BOT_TOKEN=
```

- `TELEGRAM_BOT_TOKEN` - The token provided by BotFather.

3. Create a new Telegram chat, add the bot, and it will remember the group for notifications.
4. To receive notifications for specific categories, use the `/categ` command in the chat.
5. You can also manage channels via the Django admin panel under the Bot section.

---

## Model API

For external model API calls, we use [Replicate.com](https://replicate.com/) as a cost-effective alternative to ChatGPT.

---

## REST API Interface

The REST API is built using the `django-rest-framework`. Documentation is automatically generated using Swagger and is available at `/swagger-ui`.

---

## Infrastructure

For project to be online, we've setup two remote machines for environments `stage` и `prod`.
They have identical configurations, and the project is started in the similar way as you would run it locally:

```
docker compose -f docker-compose.prod.yaml pull
docker-compose -f docker-compose.prod.yaml -d
```

More deployment details in [deploy.yml](.github/workflows/deploy.yml).

> [!NOTE]
> Working directory for the project is `/opt/services/neuro-parser`. 
> Should the value change, you can look it up in `$DEPLOY_LOCATION` at [deploy.yml](.github/workflows/deploy.yml).

> [!WARNING] Beware!
> Working directory of `github-actions` (`/home/github-actions/_work/neuro-parser`) is only used to clone project's source code.
> It's not used for running the project and shouldn't be used by anyone to do so.

### Типовые операции на серверах

- **An error has occured in the environment, so we need to look at logs**
  
  ```bash
  # a particular container
  # web - server (admin section), bot - TG-bot, celery - tasks in queues
  docker logs neuro-parser-web-1
  # or
  cd /opt/services/neuro-parser
  docker-compose -f docker-compose.prod.yml logs -f
  ```

- **Need to test a script inside the container**
  
  ```bash
  # web - server (admin section), bot - TG-bot, celery - tasks in queues
  docker exec -it neuro-parser-web-1 bash
  # or
  cd /opt/services/neuro-parser
  docker-compose -f docker-compose.prod.yml exec -it web bash
  ```

- **No space left. Server spams with `No space left on device` messages.**

  Most likely the space finished due to frequent rebuilds or image pulls. We periodically clean up the space from unused images and containers, but it might not be sufficient sometimes. You can do that manually:

  ```bash
  docker container prune -f
  docker image prune -af
  # check disk usage
  df -h
  ```

---

## Contributing

We welcome contributions from the community. Please follow the guidelines in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

---

## Contact

If you have any questions or need further assistance, feel free to contact us at info@antijob.net.
