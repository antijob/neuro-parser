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

If you have questions or need further assistance, please contact us at [antijob@riseup.net].

Thank you for your contributions to the Neural Parser project!
