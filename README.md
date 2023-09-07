A neural parser is a tool for parsing and analyzing news and content to search for incidents related to a specific topic.

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


## Running local

Firstly modify `config/.env` and create database and replase to apps.

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

Firstly modify `config/.env` and create database and replase to apps.

Run `docker-compose -f docker-compose.prod.yaml up -d` inside root directory for start local container.

After that run migrations inside container:

```
docker <PYTHON_CONTAINER_ID> python manage.py migrate
```
