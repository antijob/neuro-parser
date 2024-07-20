FROM python:3.9-slim

# setup environments
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/tmp
ENV PDM_CHECK_UPDATE=false

# setup workdir
WORKDIR /code

# install system dependencies for final stage
RUN apt-get update && \
  apt-get install -y --no-install-recommends gcc libxml2-dev python3-lxml libxslt-dev libxslt1-dev python3-dev libjpeg-dev libtiff-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev postgresql-server-dev-all && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

# install PDM
RUN pip install -U pip && pip install pdm

# copy files
COPY pyproject.toml pdm.lock README.md /code/

# generate requirements.txt
RUN pdm export --no-hashes -o requirements.txt

# install requirements.txt
RUN pip install -r requirements.txt
