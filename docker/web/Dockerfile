# syntax=docker/dockerfile:1.0.0-experimental #Experemental for fasters building

# Use a base image with Python
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TRANSFORMERS_CACHE=/tmp
ENV PDM_CHECK_UPDATE=false


# Setup workdir
WORKDIR /code

# Install system dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
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
    rm -rf /var/lib/apt/lists/* && \
    apt-get update --fix-missing
# Install PDM
RUN pip install -U pip && \
    pip install pdm && \
    pip install nltk

# Install NLTK dependencies
RUN python -m nltk.downloader punkt && \
    python -m nltk.downloader stopwords


# Copy dependency management files first to leverage Docker cache
COPY pyproject.toml pdm.lock /code/

# Which groups to install in to the container. If none, will not install additional groups.
# Pass as docker-compose build --build-arg PDM_DEPENDENCY_GROUPS="groupA groupB" or
#   docker build ... --build-arg PDM_DEPENDENCY_GROUPS=""
# By default will build with all groups, including `torch` group, which requires GPU
ARG PDM_DEPENDENCY_GROUPS=:all
# Generate requirements.txt
# PDM_GROUP_FLAGS is prefixing everything in PDM_DEPENDENCY_GROUPS
RUN export PDM_GROUP_FLAGS=${PDM_DEPENDENCY_GROUPS:+$(echo "$PDM_DEPENDENCY_GROUPS" | sed -E "s/( |^)/ -G /g")} && \
    pdm export --no-hashes ${PDM_GROUP_FLAGS} -o requirements.txt

# Install dependencies and caching
RUN --mount=type=cache,target=/root/.cache \
  pip install -r requirements.txt

# Add the rest of the code
ADD . /code/
