#!/usr/bin/env sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
case "$repo_root" in
  /mnt/d/*|/d/*|D:/*|d:/*) ;;
  *) echo "Refusing to delete project data outside disk D:." >&2; exit 1 ;;
esac

data_dir="$repo_root/.docker-data"
case "$data_dir" in
  "$repo_root/.docker-data") rm -rf -- "$data_dir" ;;
  *) echo "Refusing unexpected data path: $data_dir" >&2; exit 1 ;;
esac
