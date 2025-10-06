#!/usr/bin/env bash
set -euo pipefail

# Usage: run.sh "command to run"
CMD_TO_RUN="$*"
# Debug flag: RUN_DEBUG=1 enables verbose logs
RUN_DEBUG="${RUN_DEBUG:-}"
debug() { if [ -n "$RUN_DEBUG" ]; then echo "[run.sh] $*" 1>&2; fi }
debug "cwd=$(pwd) args=${CMD_TO_RUN}"

# Enable shell tracing when debugging
if [ -n "$RUN_DEBUG" ]; then
  set -x
fi

# Map GH_PAT -> GITHUB_TOKEN if only GH_PAT is present
if [ -z "${GITHUB_TOKEN:-}" ] && [ -n "${GH_PAT:-}" ]; then
  export GITHUB_TOKEN="${GH_PAT}"
  debug "Mapped GH_PAT -> GITHUB_TOKEN"
fi

# Detect if running inside container (rely on /.dockerenv; allow explicit override via FORCE_IN_DOCKER)
if [ -f "/.dockerenv" ] || [ "${FORCE_IN_DOCKER:-}" = "1" ]; then
  # Ensure /project is a bind mount to host
  if grep -q " /project " /proc/self/mountinfo || mount | grep -q " on /project "; then
    debug "Inside container with bind mount detected; executing directly"
    # Execute in /project with strict shell; ensure deps if missing
    if [ -n "$RUN_DEBUG" ]; then
      exec bash -lc "set -euo pipefail; echo '[container] PWD='\"$PWD\"; [ -d /project ] && cd /project; which poetry || true; poetry --version || true; \
        echo '[container] ensuring poetry deps...'; missing=0; \
        poetry run python -c 'import frictionless' 2>/dev/null || missing=1; \
        poetry run python -c 'import scripts.publish_ckan' 2>/dev/null || missing=1; \
        if [ \"\$missing\" = 1 ]; then poetry install --only=main --no-root; fi; \
        echo '[container] running:' \"$CMD_TO_RUN\"; \
        if [[ \"$CMD_TO_RUN\" == 'poetry run publish-ckan'* ]]; then \
          eval \"poetry run python -m scripts.publish_ckan${CMD_TO_RUN#poetry run publish-ckan}\"; \
        else \
          eval \"$CMD_TO_RUN\"; \
        fi"
    else
      exec bash -lc "set -euo pipefail; [ -d /project ] && cd /project; missing=0; \
        poetry run python -c 'import frictionless' 2>/dev/null || missing=1; \
        poetry run python -c 'import scripts.publish_ckan' 2>/dev/null || missing=1; \
        if [ \"\$missing\" = 1 ]; then poetry install --only=main --no-root; fi; \
        if [[ \"$CMD_TO_RUN\" == 'poetry run publish-ckan'* ]]; then \
          eval \"poetry run python -m scripts.publish_ckan${CMD_TO_RUN#poetry run publish-ckan}\"; \
        else \
          eval \"$CMD_TO_RUN\"; \
        fi"
    fi
    exit 0
  else
    echo "❌ /project não está montado como bind. Rode 'make docker' para entrar com bind ou execute 'make' no host." 1>&2
    exit 1
  fi
fi

# Running on host: ensure docker variables are set; fallback to config.mk
# Auto-detect .env if DOCKER_ENV_FILE not provided
DOCKER_ENV_FILE_OPT="${DOCKER_ENV_FILE:-}"
if [ -z "${DOCKER_ENV_FILE_OPT}" ] && [ -f ./.env ]; then
  DOCKER_ENV_FILE_OPT="--env-file .env"
  debug "Auto-detected .env -> adding --env-file .env"
fi

if [ -z "${DOCKER_USER:-}" ] || [ -z "${DOCKER_IMAGE:-}" ] || [ -z "${DOCKER_TAG:-}" ]; then
  if [ -f "config.mk" ]; then
    # shellcheck disable=SC2046
    eval $(awk -F '=' '/^(DOCKER_USER|DOCKER_IMAGE|DOCKER_TAG)=/ {gsub(/\r/,""); printf("export %s=%s\n", $1, $2)}' config.mk)
    debug "Loaded docker vars from config.mk: DOCKER_USER=${DOCKER_USER:-}, DOCKER_IMAGE=${DOCKER_IMAGE:-}, DOCKER_TAG=${DOCKER_TAG:-}"
  fi
fi

DOCKER_USER_ENV="${DOCKER_USER:?DOCKER_USER not set}"
DOCKER_IMAGE_ENV="${DOCKER_IMAGE:?DOCKER_IMAGE not set}"
DOCKER_TAG_ENV="${DOCKER_TAG:?DOCKER_TAG not set}"
debug "docker run with image ${DOCKER_USER_ENV}/${DOCKER_IMAGE_ENV}:${DOCKER_TAG_ENV}"
debug "env-file opt: '${DOCKER_ENV_FILE_OPT}'"
debug "command: ${CMD_TO_RUN}"

# Extra docker run flags (non-interactive by default; no TTY unless requested)
EXTRA_FLAGS="${DOCKER_RUN_EXTRA:-}"
if [ -z "${EXTRA_FLAGS}" ]; then
  EXTRA_FLAGS=""
fi
debug "extra flags: '${EXTRA_FLAGS}'"

docker run --rm ${EXTRA_FLAGS} ${DOCKER_ENV_FILE_OPT} \
  -e GITHUB_TOKEN -e GH_PAT -e CKAN_HOST -e CKAN_KEY \
  -e RUN_DEBUG \
  -v "$(pwd)":/project \
  -w /project \
  "${DOCKER_USER_ENV}/${DOCKER_IMAGE_ENV}:${DOCKER_TAG_ENV}" \
  bash -lc "set -euo pipefail; echo '[container] PWD='\"$PWD\"; which poetry || true; poetry --version || true; echo '[container] running:' \"$CMD_TO_RUN\"; $CMD_TO_RUN; echo '[container] ls datapackages:'; ls -lah datapackages || true" </dev/null


