#!/usr/bin/env bash
set -euo pipefail

# Choose one:
#   linux/arm64  -> 64-bit Raspberry Pi OS / Debian arm64
#   linux/arm/v7 -> 32-bit Raspberry Pi OS armhf-like (you would also adjust PKG_ARCH)
PLATFORM="${PLATFORM:-linux/arm64}"

# For linux/arm/v7 you likely want: PKG_ARCH=armhf (or armv7l depending on repo conventions)
PKG_ARCH="${PKG_ARCH:-arm64}"

# Ensure a buildx builder exists (idempotent-ish)
docker buildx create --name smsdoorman-builder --use --bootstrap --buildkitd-config ./misc/buildkitd.toml >/dev/null 2>&1 || docker buildx use smsdoorman-builder

docker buildx build \
  --build-arg PKG_ARCH="${PKG_ARCH}" \
  --output type=local,dest=dist \
  --platform "${PLATFORM}" \
  -t sms-doorman-shell:local \
  --load \
  .

docker run --rm -v "$PWD/artifacts:/artifacts" --platform ${PLATFORM} -it sms-doorman-shell:local /bin/bash

