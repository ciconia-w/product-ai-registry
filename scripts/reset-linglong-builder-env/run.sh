#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="${1:-$(date +%Y%m%d-%H%M%S)}"
MOUNT_SNAPSHOT="/tmp/dcc-linglong-mounts-${STAMP}.txt"

echo "==> stopping lingering Linglong-related processes"
pkill -f "ll-builder build" || true
pkill -f "ll-builder export" || true
pkill -f "build_from_project.py --input ${ROOT_DIR}" || true
pkill -f "ll-cli run org.deepin.deepin-color-correction" || true
pkill -f "/deepin-color-correction($| )" || true

echo "==> collecting Linglong mounts"
mount > /tmp/dcc-all-mounts-${STAMP}.txt
grep -E "linglong-builder|deepin-color-correction/linglong/cache|/tmp/linglong-runtime-0|/run/user/[0-9]+/linglong" \
  /tmp/dcc-all-mounts-${STAMP}.txt \
  | awk '{print $3}' \
  | sort -u > "${MOUNT_SNAPSHOT}" || true

if [[ -s "${MOUNT_SNAPSHOT}" ]]; then
  echo "==> unmounting stale Linglong mounts"
  while read -r mp; do
    [[ -n "${mp}" ]] || continue
    sudo umount -l "${mp}" || true
  done < "${MOUNT_SNAPSHOT}"
fi

echo "==> backing up local Linglong caches"
for path in \
  "${HOME}/.cache/linglong-builder" \
  "${ROOT_DIR}/linglong" \
  "/tmp/linglong-runtime-0"
do
  if [[ -e "${path}" ]]; then
    if [[ "${path}" == /tmp/* ]]; then
      sudo mv "${path}" "${path}.bak-${STAMP}"
    else
      mv "${path}" "${path}.bak-${STAMP}"
    fi
    echo "moved ${path} -> ${path}.bak-${STAMP}"
  fi
done

mkdir -p "${HOME}/.cache/linglong-builder" "${ROOT_DIR}/linglong"

echo "==> reset complete"
echo "stamp=${STAMP}"
