UPD on 06.07.23
I deleted almost all previous stuff cause it's not very usable now

## Development

For managing python packages we use ['poetry'](https://python-poetry.org/docs/)

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

## Running

Firstly modify `config/.env` and create database and replase to apps.


After that run migrations:

```
~ ./manage migrate
```

If you want to run it on local machine, just:

```
~ make runserver
```

**Note**: Don't forget about migrations.

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

