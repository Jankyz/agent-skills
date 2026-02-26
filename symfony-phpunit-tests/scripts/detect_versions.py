#!/usr/bin/env python3
import json
import os
import re
import sys


def read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def extract_version(constraint):
    if not constraint:
        return None
    match = re.search(r"(\d+)(?:\.(\d+))?", str(constraint))
    if not match:
        return None
    major = match.group(1)
    minor = match.group(2)
    return f"{major}.{minor}" if minor is not None else major


def find_pkg_version(lock_data, name):
    for section in ("packages", "packages-dev"):
        for pkg in lock_data.get(section, []):
            if pkg.get("name") == name:
                return pkg.get("version")
    return None


def main():
    base_path = sys.argv[1] if len(sys.argv) > 1 else "."
    composer_path = os.path.join(base_path, "composer.json")
    if not os.path.exists(composer_path):
        print(json.dumps({"error": "composer.json not found"}))
        return 1

    composer = read_json(composer_path)
    require = composer.get("require", {})
    require_dev = composer.get("require-dev", {})
    config = composer.get("config", {})
    platform = config.get("platform", {})

    php_platform = platform.get("php")
    php_constraint = require.get("php")
    php_version = extract_version(php_platform) or extract_version(php_constraint)

    phpunit_constraint = require_dev.get("phpunit/phpunit")
    phpunit_bridge_constraint = require_dev.get("symfony/phpunit-bridge")
    symfony_constraint = (
        require.get("symfony/framework-bundle")
        or require.get("symfony/symfony")
        or require_dev.get("symfony/framework-bundle")
    )

    lock_path = os.path.join(base_path, "composer.lock")
    lock_data = read_json(lock_path) if os.path.exists(lock_path) else {}
    phpunit_locked = find_pkg_version(lock_data, "phpunit/phpunit")
    symfony_locked = find_pkg_version(lock_data, "symfony/framework-bundle") or find_pkg_version(
        lock_data, "symfony/symfony"
    )

    docker_image = f"wodby/php:{php_version}" if php_version else None

    result = {
        "php_platform": php_platform,
        "php_constraint": php_constraint,
        "php_version_detected": php_version,
        "phpunit_constraint": phpunit_constraint,
        "phpunit_bridge_constraint": phpunit_bridge_constraint,
        "phpunit_version_locked": phpunit_locked,
        "symfony_constraint": symfony_constraint,
        "symfony_version_locked": symfony_locked,
        "docker_image": docker_image,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
