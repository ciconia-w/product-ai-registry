#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "usage: $0 <capability-type> <capability-id> <target-repo-root>"
  exit 2
fi

TYPE="$1"
ID="$2"
TARGET_ROOT="$3"

echo "[install-project-capability] type=${TYPE}"
echo "[install-project-capability] id=${ID}"
echo "[install-project-capability] target=${TARGET_ROOT}"
echo "[install-project-capability] placeholder skeleton only"
echo "[install-project-capability] TODO: resolve adapter, choose materialization mode, copy namespaced files"
