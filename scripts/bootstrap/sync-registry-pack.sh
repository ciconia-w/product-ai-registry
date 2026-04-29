#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: $0 <registry-url> <pack-id>"
  exit 2
fi

REGISTRY_URL="$1"
PACK_ID="$2"

echo "[sync] registry=${REGISTRY_URL}"
echo "[sync] pack=${PACK_ID}"
echo "[sync] placeholder skeleton only"
echo "[sync] TODO: read manifest, resolve pack, and materialize items"
