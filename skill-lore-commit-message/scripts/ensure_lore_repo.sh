#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Initialize Lore in the current git repository if needed.

Usage:
  ensure_lore_repo.sh [--lore-bin <command>]

Options:
  --lore-bin <cmd>  Command used to invoke Lore. Examples: "lore", "npx lore"
  --help            Show this help
EOF
}

lore_bin=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lore-bin)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --lore-bin" >&2
        exit 1
      fi
      lore_bin="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  echo "Run this script inside a git repository." >&2
  exit 1
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "${repo_root}"

if [[ -f ".lore/config.toml" ]]; then
  echo "Lore is already initialized at ${repo_root}/.lore/config.toml"
  exit 0
fi

if [[ -z "${lore_bin}" ]]; then
  if command -v lore >/dev/null 2>&1; then
    lore_bin="lore"
  elif command -v npx >/dev/null 2>&1; then
    lore_bin="npx lore"
  else
    echo "Could not find lore or npx. Install lore-protocol first." >&2
    exit 1
  fi
fi

echo "Initializing Lore in ${repo_root} using: ${lore_bin}"
read -r -a lore_cmd <<< "${lore_bin}"
"${lore_cmd[@]}" init
