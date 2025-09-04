#!/usr/bin/env bash
set -euo pipefail

# Deployment script for baes_docker_shura
# - Performs a safe, project-scoped cleanup (containers/volumes)
# - Rebuilds/pulls and restarts the stack
#
# Notes:
# - Uses COMPOSE_PROJECT_NAME if set; otherwise defaults to "baes" to scope cleanup.
# - Assumes docker (with Compose V2) is installed on the server.

PROJECT_NAME=${COMPOSE_PROJECT_NAME:-baes}
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT_DIR"

echo "[deploy] Project dir: $ROOT_DIR"
echo "[deploy] Compose project name: $PROJECT_NAME"

compose() {
  # Prefer docker compose (V2); fallback to docker-compose if needed
  if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    docker compose -p "$PROJECT_NAME" "$@"
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose -p "$PROJECT_NAME" "$@"
  else
    echo "[deploy] ERROR: Neither 'docker compose' nor 'docker-compose' found on server." >&2
    exit 1
  fi
}

preflight() {
  echo "[deploy] Preflight checks (RAM/Swap/CPU AVX)"
  # Memory check
  if command -v free >/dev/null 2>&1; then
    MEM_TOTAL_MB=$(free -m | awk '/Mem:/ {print $2}')
    SWAP_TOTAL_MB=$(free -m | awk '/Swap:/ {print $2}')
    echo "[deploy] Host memory: ${MEM_TOTAL_MB} MiB RAM, ${SWAP_TOTAL_MB} MiB swap"
    if [ "${MEM_TOTAL_MB}" -lt 1900 ] && [ "${SWAP_TOTAL_MB}" -lt 1024 ]; then
      cat >&2 <<'EOF'
[deploy][WARN] Low memory detected and no/low swap.
- SQL Server (Linux) typically requires >= 2 GiB RAM or sufficient swap. With <2 GiB RAM and 0 swap, the mssql container may crash (SIGABRT) during startup.
- This explains why it works locally (more RAM/swap) but fails on the server.
Suggested fix (Ubuntu/Debian as root):
  fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile none swap sw 0 0' >> /etc/fstab
Then re-run the deploy.
EOF
    fi
  fi
  # CPU AVX check (best-effort)
  if command -v lscpu >/dev/null 2>&1; then
    if ! lscpu | grep -iq avx; then
      echo "[deploy][WARN] CPU AVX not detected. SQL Server requires AVX-capable CPU and may fail to start." >&2
    fi
  fi
}

preflight

# Stop and remove current stack, including volumes defined by this compose file
echo "[deploy] Bringing down current stack (including volumes and orphans)"
compose down --remove-orphans -v || true

# Extra safety cleanup scoped to this compose project
# Remove containers with label com.docker.compose.project=$PROJECT_NAME
if command -v docker >/dev/null 2>&1; then
  echo "[deploy] Removing lingering containers for project $PROJECT_NAME (if any)"
  docker ps -aq --filter "label=com.docker.compose.project=$PROJECT_NAME" | xargs -r docker rm -f || true

  echo "[deploy] Removing lingering volumes for project $PROJECT_NAME (if any)"
  docker volume ls -q --filter "label=com.docker.compose.project=$PROJECT_NAME" | xargs -r docker volume rm -f || true

  echo "[deploy] Pruning unused networks (safe)"
  docker network prune -f || true

  echo "[deploy] Pruning dangling/unused images (safe)"
  docker image prune -af || true

  echo "[deploy] Removing any containers with fixed names that may conflict"
  FIXED_NAMES="mssql-test api-test front-test edge-test"
  for name in $FIXED_NAMES; do
    ID=$(docker ps -aq -f name="^/$name$")
    if [ -n "$ID" ]; then
      echo "[deploy] Force removing lingering container: $name ($ID)"
      docker rm -f $ID || true
    fi
  done
fi

# Build and start new stack
# Pull if images are referenced by tag from a registry
# If you build locally, build --pull ensures base images are fresh.
echo "[deploy] Pulling images (if any)"
compose pull || true

echo "[deploy] Building images (with --pull to refresh bases)"
compose build --pull

echo "[deploy] Starting stack"
compose up -d

echo "[deploy] Deployment finished successfully."