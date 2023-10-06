# Neural Parser

A neural parser is a tool for parsing and analyzing news and content to search for incidents related to a specific topic.

## Development

### Managing Python Packages

For managing Python packages, we use [Poetry](https://python-poetry.org/docs/):

```
# install everything
poetry install

# update 
poetry update

# go to venv
poetry shell

# generate requirements.txt
poetry export --format requirements.txt --without-hashes --output requirements.txt
```

docker still use generated requirements.txt file
git should contain both pyproject.toml and poetry.lock files 


## Running local

Firstly modify `config/.env`, create database and replace to apps.

Run `docker-compose up -d` inside root directory for start local container.

After that run migrations inside container:

```
docker <PYTHON_CONTAINER_ID> python manage.py migrate
```

Add for you `/etc/hosts` file record which resolve domain for local traefik

```
127.0.0.1 report.local
```

Open admin panel in `http://report.local:8008/s/ecret/admin`

Or use api `http://report.local:8008/api`


## Running production

Firstly modify `config/.env` and create database and replace to apps.

Run `docker-compose -f docker-compose.prod.yaml up -d` inside root directory for start local container.

After that run migrations inside container:

```
docker <PYTHON_CONTAINER_ID> python manage.py migrate
```

## Contributing

We welcome contributions from the community. If you would like to contribute to this project, please follow the guidelines in the [CONTRIBUTING.md](CONTRIBUTING.md) file.

## Contact

If you have questions or need further assistance, please contact us at info@antijob.net.

## Telegram bot
You can use telegram bot to receive notifications about new incidents.

To install it you need to register new bot with BotFather
Then add settings to .env file
```
TELEGRAM_BOT_TOKEN=
TELEGRAM_BOT_NAME=
TELEGRAM_BOT_URL=
```
Token from BotFather, name that you gave to the bot and url for web hooks. Default url - yoursite.com/bot
After that you need to create new telegram bot and and add bot there. That's all bot remember that group 
and will send notifications there. If you want recieve notifications only for some of existing categories
use command ```/categ``` for bot settings. 
Also you can go to Django admin and check Bot section to explore what channels are saved. 

Thank you for your contributions to the Neural Parser project!

