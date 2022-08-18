FROM alpine:edge

ENTRYPOINT ["/sbin/tini"]
WORKDIR /app

ENV POETRY_VERSION=1.1.4 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  QT_QPA_PLATFORM='offscreen' \
  XDG_RUNTIME_DIR='/tmp/runtime-$USER'

# Order is very relevant!!! // Sorted by chance of changes (less frequent first)
# Each step is cached on the buildhost, so right commands order prevents it from unneded rebuilds
# Change in any step will invalidate cache of all the next ones


RUN sed -e '/community/{p;s@v[^/]*/@edge/@;s@community@testing@}' -i /etc/apk/repositories && \
    apk update && \
    apk upgrade && \
    apk add \
        curl \
        sed \
        ca-certificates \
        zsh \
        tini \
        postgresql-dev \
        libffi-dev \
        libxml2-dev \
        libxslt-dev \
        jpeg-dev \
        gcc \
        dcron \
        postgresql-client \
        libstdc++ musl-dev python3-dev cython \
        py3-cryptography \
        py3-joblib \
        py3-scikit-learn \
        wkhtmltopdf \
        unit-python3 \
        unit \
        ttf-liberation \
    && \
    chown 65534:65534 /app && \
    curl https://bootstrap.pypa.io/get-pip.py -LSso get-pip.py && \
    python3 get-pip.py && \
    pip install "poetry==$POETRY_VERSION" && poetry --version && \
    mkdir -p /app/public/uploads && \
    fc-cache -fv

COPY /meta/configs/unit.conf.json /var/lib/unit/conf.json

COPY --chown=65534:65534 /poetry.lock /pyproject.toml /app/

RUN poetry install --no-interaction --no-ansi

COPY /meta/sh /bin/

COPY --chown=65534:65534 /manage.py /app/
COPY --chown=65534:65534 /public /app/public/
COPY --chown=65534:65534 /server /app/server/

# vim: ft=dockerfile ts=2 sw=2
