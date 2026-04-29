#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_ID="org.deepin.deepin-color-correction"
DIST_UAB="${ROOT_DIR}/dist/deepin-color-correction_x86_64_0.1.0.6_main.uab"
DIST_LAYER="${ROOT_DIR}/dist/${APP_ID}_0.1.0.6_x86_64_binary.layer"

cd "${ROOT_DIR}"

echo "==> resetting local Linglong builder environment"
"${ROOT_DIR}/scripts/reset-linglong-builder-env.sh"

echo "==> rebuilding layer and UAB using repo-converged script"
"${ROOT_DIR}/scripts/build-linglong.sh"

echo "==> quick validation"
"${DIST_UAB}" --print-meta
rm -rf /tmp/dcc-uab-shortest-path-check
mkdir -p /tmp/dcc-uab-shortest-path-check
"${DIST_UAB}" --extract=/tmp/dcc-uab-shortest-path-check >/dev/null
find /tmp/dcc-uab-shortest-path-check/layers/${APP_ID}/binary/files/lib/python3/dist-packages \
  -maxdepth 1 \
  \( -type d -o -type f \) \
  | grep -E "PySide6|shiboken6" \
  | sort
sha256sum "${DIST_UAB}"

echo "==> done"
echo "layer=${DIST_LAYER}"
echo "uab=${DIST_UAB}"
