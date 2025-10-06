#!/usr/bin/env bash
set -euo pipefail

# Usage: run.sh "command to run"
CMD_TO_RUN="$*"
# Debug flag: RUN_DEBUG=1 enables verbose logs
RUN_DEBUG="${RUN_DEBUG:-}"
debug() { if [ -n "$RUN_DEBUG" ]; then echo "[run.sh] $*" 1>&2; fi }
debug "cwd=$(pwd) args=${CMD_TO_RUN}"

# Map GH_PAT -> GITHUB_TOKEN if only GH_PAT is present
if [ -z "${GITHUB_TOKEN:-}" ] && [ -n "${GH_PAT:-}" ]; then
  export GITHUB_TOKEN="${GH_PAT}"
  debug "Mapped GH_PAT -> GITHUB_TOKEN"
fi

# Detect if running inside container
if [ -f "/.dockerenv" ] || [ "${IN_DOCKER:-}" = "1" ]; then
  # Ensure /project is a bind mount to host
  if grep -q " /project " /proc/self/mountinfo || mount | grep -q " on /project "; then
    debug "Inside container with bind mount detected; executing directly"
    exec bash -lc "$CMD_TO_RUN"
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

# Extra docker run flags (e.g., -it for interactive TTY)
EXTRA_FLAGS="${DOCKER_RUN_EXTRA:-}"
if [ -z "${EXTRA_FLAGS}" ] && [ -n "${RUN_DEBUG}" ]; then
  # when debugging, prefer TTY for better log flushing
  EXTRA_FLAGS="-t"
fi
debug "extra flags: '${EXTRA_FLAGS}'"

docker run --rm ${EXTRA_FLAGS} ${DOCKER_ENV_FILE_OPT} \
  -e GITHUB_TOKEN -e GH_PAT -e CKAN_HOST -e CKAN_KEY \
  -v "$(pwd)":/project \
  "${DOCKER_USER_ENV}/${DOCKER_IMAGE_ENV}:${DOCKER_TAG_ENV}" \
  bash -lc "$CMD_TO_RUN"


