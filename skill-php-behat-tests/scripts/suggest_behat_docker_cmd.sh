#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Suggest a docker command for running Behat in this repo.

Usage:
  scripts/suggest_behat_docker_cmd.sh [--config behat.yml.dist] [--path features/foo.feature[:line]] [--image php-image]

Notes:
  - Detection is best-effort. Always verify PHP version in the repo if unsure.
  - If --image is omitted, the script tries to infer it from compose/Dockerfile/composer.json.
EOF
}

config=""
path="features"
image=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      config="${2:-}"
      shift 2
      ;;
    --path)
      path="${2:-}"
      shift 2
      ;;
    --image)
      image="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

detect_from_compose() {
  local f line img
  for f in compose.yml docker-compose.yml compose.dist.yml docker-compose.dist.yml; do
    [[ -f "$f" ]] || continue
    # Pick first image entry that looks like a PHP runtime.
    line="$(awk '/^[[:space:]]*image:[[:space:]]*/ {print $0; exit}' "$f" 2>/dev/null || true)"
    img="$(printf '%s' "$line" | sed -E 's/^[[:space:]]*image:[[:space:]]*//; s/[[:space:]]+#.*$//; s/^["'\'']?//; s/["'\'']?$//')"
    if [[ -n "$img" && "$img" == *php* ]]; then
      echo "$img"
      return 0
    fi
  done
  return 1
}

detect_php_version() {
  local v

  if [[ -f composer.json ]]; then
    v="$(python3 - <<'PY' 2>/dev/null || true
import json, re
with open("composer.json", "r", encoding="utf-8") as f:
    data = json.load(f)
php = (data.get("config", {}).get("platform", {}) or {}).get("php") or (data.get("require", {}) or {}).get("php") or ""
m = re.search(r"(\\d+\\.\\d+)", str(php))
print(m.group(1) if m else "")
PY
)"
    if [[ -n "$v" ]]; then
      echo "$v"
      return 0
    fi
  fi

  if [[ -f Dockerfile ]]; then
    v="$(awk -F= '/^ARG[[:space:]]+PHP_VERSION=/{print $2; exit}' Dockerfile 2>/dev/null | tr -d '[:space:]' || true)"
    if [[ -n "$v" ]]; then
      # Normalize to major.minor when possible.
      if [[ "$v" =~ ^([0-9]+)\.([0-9]+) ]]; then
        echo "${BASH_REMATCH[1]}.${BASH_REMATCH[2]}"
        return 0
      fi
      echo "$v"
      return 0
    fi
  fi

  return 1
}

if [[ -z "$config" ]]; then
  if [[ -f behat.yml.dist ]]; then
    config="behat.yml.dist"
  elif [[ -f behat.yml ]]; then
    config="behat.yml"
  else
    config=""
  fi
fi

if [[ -z "$image" ]]; then
  image="$(detect_from_compose || true)"
fi

php_version=""
php_version="$(detect_php_version || true)"

if [[ -z "$image" ]]; then
  if [[ -n "$php_version" ]]; then
    image="wodby/php:${php_version}"
  else
    image="<php-image>"
  fi
fi

config_arg=""
if [[ -n "$config" ]]; then
  config_arg="-c $config"
fi

echo "docker run --rm -v \"\$PWD\":/app -w /app $image bin/behat $config_arg $path"
