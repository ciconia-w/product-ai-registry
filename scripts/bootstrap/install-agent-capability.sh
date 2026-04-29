#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "usage: $0 <agent-id> <capability-type> <capability-id>"
  exit 2
fi

AGENT_ID="$1"
TYPE="$2"
ID="$3"

echo "[install-agent-capability] agent=${AGENT_ID}"
echo "[install-agent-capability] type=${TYPE}"
echo "[install-agent-capability] id=${ID}"
echo "[install-agent-capability] placeholder skeleton only"
echo "[install-agent-capability] TODO: load adapters/${AGENT_ID}/adapter.yaml and materialize safely"
