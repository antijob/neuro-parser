###########
# BUILDER #
###########

# pull official base image
FROM python:3.9-slim as builder

# set work directory
WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install system dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  gcc \
  libxml2-dev \
  python3-lxml \
  libxslt-dev \
  libxslt1-dev \
  python3-dev \
  libjpeg-dev \
  libtiff-dev \
  zlib1g-dev \
  libfreetype6-dev \
  liblcms2-dev \
  libwebp-dev \
  postgresql-server-dev-all && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# install pip and lint
RUN pip install --upgrade pip setuptools wheel && \
  pip install flake8==6.0.0

# install PDM
RUN pip install -U pip && pip install pdm

# copy project files
COPY pyproject.toml pdm.lock README.md ./

# install python dependencies
RUN pdm install --check --prod --no-editable

#########
# FINAL #
#########

# pull official base image
FROM python:3.9-slim

# create directory for the app user
RUN mkdir -p /home/github-actions && \
  addgroup --system github-actions && \
  adduser --system --ingroup github-actions github-actions

# create the appropriate directories
ENV HOME=/home/github-actions
ENV APP_HOME=/home/github-actions/code
ENV TRANSFORMERS_CACHE=/tmp
WORKDIR $APP_HOME

# retrieve packages from build stage
COPY --from=builder /code/.venv/ $APP_HOME/.venv
ENV PATH="$APP_HOME/.venv/bin:$PATH"

# download nltk data
RUN python -m nltk.downloader punkt && \
  python -m nltk.downloader stopwords

# copy project
COPY . $APP_HOME

# chown all the files to the app user
RUN chown -R github-actions:github-actions $APP_HOME

# change to the app user
USER github-actions
