#!/usr/bin/env sh
set -eu

if [ ! -f .env ]; then
  echo "Missing .env. Copy .env.example to .env, then retry." >&2
  exit 1
fi

set -a
. ./.env
set +a
exec sh scripts/bootstrap.sh
