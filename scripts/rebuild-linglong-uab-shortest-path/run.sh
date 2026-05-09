#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(pwd)"

find_repo_root() {
  local dir="${PWD}"
  while [[ "${dir}" != "/" ]]; do
    if [[ -f "${dir}/linglong.yaml" || -d "${dir}/scripts" ]]; then
      echo "${dir}"
      return 0
    fi
    dir="$(dirname "${dir}")"
  done
  return 1
}

if repo_root="$(find_repo_root)"; then
  ROOT_DIR="${repo_root}"
fi

cd "${ROOT_DIR}"

if [[ ! -f "${ROOT_DIR}/linglong.yaml" ]] && ! find "${ROOT_DIR}/scripts" -maxdepth 1 -type f -name 'build-linglong*.sh' >/dev/null 2>&1; then
  echo "blocked: no linglong.yaml or build-linglong*.sh found under ${ROOT_DIR}" >&2
  exit 1
fi

echo "==> resetting local Linglong builder environment"
if [[ -x "${ROOT_DIR}/scripts/reset-linglong-builder-env.sh" ]]; then
  "${ROOT_DIR}/scripts/reset-linglong-builder-env.sh"
else
  "$(dirname "$0")/../reset-linglong-builder-env/run.sh"
fi

project_script=""
if [[ -x "${ROOT_DIR}/scripts/build-linglong.sh" ]]; then
  project_script="${ROOT_DIR}/scripts/build-linglong.sh"
else
  candidate="$(find "${ROOT_DIR}/scripts" -maxdepth 1 -type f -name 'build-linglong-*.sh' | sort | head -n 1 || true)"
  if [[ -n "${candidate}" ]]; then
    project_script="${candidate}"
  fi
fi

if [[ -n "${project_script}" ]]; then
  echo "==> rebuilding using project-native Linglong script: ${project_script}"
  "${project_script}"
else
  echo "==> rebuilding using generic linglong.yaml workflow"
  sudo env HOME="$HOME" XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}" ll-builder build -f "${ROOT_DIR}/linglong.yaml"

  app_id="$(python3 - <<'PY'
import sys, yaml
with open("linglong.yaml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)
print(data.get("package", {}).get("id", ""))
PY
)"
  app_version="$(python3 - <<'PY'
import sys, yaml
with open("linglong.yaml", "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)
print(data.get("package", {}).get("version", ""))
PY
)"
  mkdir -p "${ROOT_DIR}/dist"
  if [[ -n "${app_id}" && -n "${app_version}" ]]; then
    layer_out="${ROOT_DIR}/dist/${app_id}_${app_version}_x86_64_binary.layer"
  else
    layer_out="${ROOT_DIR}/dist/linglong-output.layer"
  fi
  sudo env HOME="$HOME" XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}" ll-builder export --layer -f "${ROOT_DIR}/linglong.yaml" || true
  if [[ -n "${app_id}" && -n "${app_version}" ]]; then
    sudo env HOME="$HOME" XDG_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}" ll-builder export -f "${ROOT_DIR}/linglong.yaml" -o "${ROOT_DIR}/dist/${app_id}_x86_64_${app_version}_main.uab" || true
  fi
fi

echo "==> generated artifacts"
find "${ROOT_DIR}/dist" -maxdepth 1 \( -name '*.layer' -o -name '*.uab' \) | sort || true
