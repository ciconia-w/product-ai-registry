#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

echo "[doctor] product-ai-registry bootstrap doctor"
echo "[doctor] repo root: ${ROOT_DIR}"

required_cli=(bash python3 curl)
missing=0

for cli in "${required_cli[@]}"; do
  if command -v "$cli" >/dev/null 2>&1; then
    echo "[ok] found CLI: $cli"
  else
    echo "[warn] missing CLI: $cli"
    missing=1
  fi
done

required_files=(
  "${ROOT_DIR}/manifest.json"
  "${ROOT_DIR}/REGISTRY.md"
  "${ROOT_DIR}/schemas/manifest.schema.json"
)

for file in "${required_files[@]}"; do
  if [[ -f "$file" ]]; then
    echo "[ok] found file: $file"
  else
    echo "[blocked] missing file: $file"
    missing=1
  fi
done

if [[ "$missing" -eq 0 ]]; then
  echo "[doctor] status=ok"
else
  echo "[doctor] status=warning"
fi
