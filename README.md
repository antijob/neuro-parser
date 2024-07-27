# Neural Parser

A neural parser is a tool for parsing and analyzing news and content to search for incidents related to a specific topic.

## Development

### Managing Python Packages

For managing Python packages, we use [PDM](https://pdm-project.org/):

```
# install all locked packages from lock file
pdm install

# resolve all dependencies and lock packages to lock file
pdm lock

# update all packages 
pdm update

# add new package to pyproject.toml
pdm add <package_name>
```

git should contain both pyproject.toml and pdm.lock files 


## Running local

Firstly create `.env` from `.env.template` and create database.

Run `docker-compose up -d` inside root directory for start local container.

Add for you `/etc/hosts` file record which resolve domain for local traefik

```
127.0.0.1 report.local
```

Open admin panel in `http://report.local/s/ecret/admin`

Or use api `http://report.local/api`


## Running production


Firstly modify `config/.env`, create database.

Run `docker-compose -f docker-compose.prod.yaml up -d` inside root directory for start local container.


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
```
* TELEGRAM_BOT_TOKEN - Token from BotFather

Then you need to create new telegram chat and add bot there. That's all bot remember that group 
and will send notifications there. If you want receive notifications only for some of existing categories
use command ```/categ``` for bot settings. 
Also you can go to Django admin and check Bot section to explore channels that are saved. 

Thank you for your contributions to the Neural Parser project!


