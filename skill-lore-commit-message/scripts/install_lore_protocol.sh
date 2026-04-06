#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Install the lore-protocol CLI.

Usage:
  install_lore_protocol.sh [--dev|--global] [--version <version>]

Options:
  --dev              Install as a local dev dependency in the current repository (default)
  --global           Install globally with npm
  --version <value>  Install a specific version, e.g. 0.1.0
  --help             Show this help
EOF
}

mode="dev"
version=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dev)
      mode="dev"
      shift
      ;;
    --global)
      mode="global"
      shift
      ;;
    --version)
      if [[ $# -lt 2 ]]; then
        echo "Missing value for --version" >&2
        exit 1
      fi
      version="$2"
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

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required." >&2
  exit 1
fi

node_major="$(node -p 'process.versions.node.split(".")[0]')"
if [[ "${node_major}" -lt 18 ]]; then
  echo "Node.js 18 or newer is required. Found $(node -v)." >&2
  exit 1
fi

package_spec="lore-protocol"
if [[ -n "${version}" ]]; then
  package_spec="${package_spec}@${version}"
fi

if [[ "${mode}" == "global" ]]; then
  echo "Installing ${package_spec} globally..."
  npm install -g "${package_spec}"
  echo "Installed. Verify with: lore --help"
  exit 0
fi

if [[ ! -f package.json ]]; then
  echo "package.json not found in the current directory. Use --global or run this from a Node repository root." >&2
  exit 1
fi

echo "Installing ${package_spec} as a dev dependency..."
npm install --save-dev "${package_spec}"
echo "Installed. Verify with: npx lore --help"
