#!/usr/bin/env bash
set -euo pipefail

# Auto-detect Docker Compose v2 plugin vs legacy docker-compose
if docker compose version >/dev/null 2>&1; then
  CMD=(docker compose)
else
  # Fallback to legacy v1
  if command -v docker-compose >/dev/null 2>&1; then
    # Ensure compatibility with newer Docker Engine API when using legacy compose v1
    export DOCKER_API_VERSION="${DOCKER_API_VERSION:-1.41}"
    # Optional: reduce noise on orphans
    export COMPOSE_IGNORE_ORPHANS="${COMPOSE_IGNORE_ORPHANS:-true}"
    CMD=(docker-compose)
  else
    echo "Error: Neither 'docker compose' (v2) nor 'docker-compose' (v1) found in PATH." >&2
    echo "Install Docker Compose v2 plugin or docker-compose v1, or run the appropriate command manually." >&2
    exit 1
  fi
fi

# Forward all arguments
"${CMD[@]}" "$@"
