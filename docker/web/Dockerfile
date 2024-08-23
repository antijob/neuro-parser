# syntax=docker/dockerfile:1.0.0-experimental #Experemental for fasters building

# Use a base image with Python
FROM python:3.9-slim

# Setup environments
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/tmp
ENV PDM_CHECK_UPDATE=false


# Setup workdir
WORKDIR /code

# Install system dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends gcc libxml2-dev python3-lxml libxslt-dev libxslt1-dev python3-dev libjpeg-dev libtiff-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev postgresql-server-dev-all && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

# Install PDM
RUN pip install -U pip && pip install pdm && pip install nltk

# Install NLTK dependencies
RUN python -m nltk.downloader punkt
RUN python -m nltk.downloader stopwords

# Copy dependency management files first to leverage Docker cache
COPY pyproject.toml pdm.lock /code/

# Generate requirements.txt
RUN pdm export --no-hashes -o requirements.txt

# Install dependencies and caching
RUN --mount=type=cache,target=/root/.cache \
  pip install -r requirements.txt