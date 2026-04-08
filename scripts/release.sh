#!/usr/bin/env sh

set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
dist_dir="$repo_root/dist"

case "${1:-build}" in
  build)
    uv build --out-dir "$dist_dir"
    ;;
  publish)
    uv publish "$dist_dir"/*
    ;;
  *)
    echo "usage: scripts/release.sh [build|publish]" >&2
    exit 2
    ;;
esac
