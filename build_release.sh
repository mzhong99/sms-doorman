#!/usr/bin/env bash
set -euxo pipefail

APP_NAME="sms-doorman"
VERSION="$(python3 -c 'import tomllib; print(tomllib.load(open("pyproject.toml","rb"))["project"]["version"])')"

# Build wheel + pinned requirements
poetry build -f wheel
poetry export -f requirements.txt --without-hashes --only main -o dist/requirements.txt

# Prepare payload (files that will be inside the .deb)
rm -rf packaging/root
mkdir -p packaging/root/opt/${APP_NAME}/artifacts
mkdir -p packaging/root/lib/systemd/system
mkdir -p packaging/root/etc/${APP_NAME}

cp -f dist/*.whl packaging/root/opt/${APP_NAME}/artifacts/
cp -f dist/requirements.txt packaging/root/opt/${APP_NAME}/artifacts/
cp -f packaging/${APP_NAME}.service packaging/root/lib/systemd/system/${APP_NAME}.service

# If there's a config, we add it in the package
[[ -f packaging/config.yaml ]] && cp -f packaging/config.yaml packaging/root/etc/${APP_NAME}/config.yaml

# Build .deb (Architecture: all)
fpm -s dir -t deb \
  -n "${APP_NAME}" \
  -v "${VERSION}" \
  -a all \
  --after-install packaging/postinst \
  --before-remove packaging/prerm \
  -d python3 \
  -d python3-venv \
  -d python3-pip \
  -C packaging/root \
  .

mkdir -p dist
mv -f ./*.deb dist/
echo "Built: $(ls -1 dist/*.deb | tail -n 1)"

