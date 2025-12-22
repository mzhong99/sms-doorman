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
    gcc \
    ruby \
    ruby-dev \
    ca-certificates \
    && gem install --no-document fpm \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry pyinstaller
RUN poetry self add poetry-plugin-export

COPY pyproject.toml /project/

# Install deps based on Poetry lock, but into the build environment
RUN poetry export -f requirements.txt --without-hashes -o /tmp/requirements.txt \
    && pip install --verbose --no-cache-dir -r /tmp/requirements.txt

COPY . /project/

CMD ["/bin/bash"]

# # Build one-file executable.
# # If your real app has dynamic imports, you will add --hidden-import / --collect-submodules flags.
# RUN pyinstaller --clean --onefile --name sms-doorman \
#     --paths /project/src /project/src/sms_doorman/main.py
# 
# ############################
# # 2) Package into .deb with fpm
# ############################
# FROM --platform=$TARGETPLATFORM debian:${DEBIAN_SUITE}-slim AS debbuild
# 
# ENV DEBIAN_FRONTEND=noninteractive
# 
# WORKDIR /pkgroot
# RUN mkdir -p /pkgroot/opt/sms_doorman/bin \
#  && mkdir -p /pkgroot/etc/systemd/system
# 
# COPY --from=pyibuild /project/dist/sms-doorman /pkgroot/opt/sms_doorman/bin/sms-doorman
# COPY packaging/sms-doorman.service /pkgroot/etc/systemd/system/sms-doorman.service
# 
# COPY packaging/postinst /scripts/postinst
# COPY packaging/prerm /scripts/prerm
# RUN chmod +x /scripts/postinst /scripts/prerm
# 
# ARG PKG_NAME=sms-doorman
# ARG PKG_VERSION=0.1.0
# ARG PKG_ARCH=arm64
# 
# RUN mkdir -p /out && \
#     fpm -s dir -t deb \
#       -n "${PKG_NAME}" \
#       -v "${PKG_VERSION}" \
#       --architecture "${PKG_ARCH}" \
#       --maintainer "Matthew Zhong <matthewzhong@logmethods.com>" \
#       --description "SMS Doorman daemon" \
#       --after-install /project/packaging/postinst \
#       --before-remove /project/packaging/prerm \
#       -C /pkgroot \
#       -p /out \
#       .
# 
# FROM scratch AS export
# COPY --from=debbuild /out/ /out/
# 
