## Prerequisites

You will need:

- `Python 3.7` (see `Pipfile` for full version)
- `PostgreSQL` with version `9.6`

## Development

When developing locally, we use:

- [`editorconfig`](http://editorconfig.org/) plugin (**required**)
- [`pipenv`](https://github.com/kennethreitz/pipenv) (**required**)
- `pycharm 2018` (recommended)

## Dependencies and Virtual Environment

```
pipenv install
```

More about [Pipenv](https://github.com/kennethreitz/pipenv) you can read at [official documentation](https://pipenv.readthedocs.io/en/latest/) of [Pipenv](https://github.com/kennethreitz/pipenv).


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

