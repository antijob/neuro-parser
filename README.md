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

