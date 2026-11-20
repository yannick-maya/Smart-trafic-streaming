#!/usr/bin/env sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
case "$repo_root" in
  /mnt/d/*|/d/*|D:/*|d:/*) ;;
  *)
    echo "This project stores persistent service data beside the checkout. Keep the checkout on disk D:." >&2
    exit 1
    ;;
esac

mkdir -p \
  "$repo_root/.docker-data/kafka" \
  "$repo_root/.docker-data/nifi/conf" \
  "$repo_root/.docker-data/nifi/state" \
  "$repo_root/.docker-data/nifi/database" \
  "$repo_root/.docker-data/nifi/flowfile" \
  "$repo_root/.docker-data/nifi/content" \
  "$repo_root/.docker-data/nifi/provenance" \
  "$repo_root/.docker-data/minio" \
  "$repo_root/.docker-data/postgres" \
  "$repo_root/.docker-data/grafana"
