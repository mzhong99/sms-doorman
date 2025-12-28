# syntax=docker/dockerfile:1.6

ARG PYTHON_VERSION=3.11
ARG DEBIAN_SUITE=trixie

############################
# 1) Build PyInstaller binary
############################
FROM --platform=$TARGETPLATFORM python:${PYTHON_VERSION}-slim-${DEBIAN_SUITE} AS pyibuild

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /project

# Add build tools only if you need them. gcc is common for native deps.
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    curl \
    ruby \
    ruby-dev \
    gcc \
    python3-dev \
    libc6-dev \
    ca-certificates \
    && gem install --no-document fpm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry
RUN poetry self add poetry-plugin-export

COPY . /project/

USER docker-user
CMD ["/bin/bash"]

