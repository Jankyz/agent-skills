---
name: symfony-phpunit-tests
description: Write and run Symfony tests with PHPUnit in Docker. Use when adding or updating tests in Symfony/PHP projects, deciding test type (unit/integration/functional), detecting PHP/PHPUnit/Symfony versions from composer.json/lock, and running phpunit then phpstan then cs-fixer in order.
---

# Symfony PHPUnit Tests

## Overview

Run tests in Symfony projects, choose the right test type and syntax for the project's PHP/PHPUnit versions,
run them via Docker, then run phpstan and cs-fixer in the agreed order.

## Workflow

### 1) Detect versions and tooling

1. Open `composer.json` and `composer.lock`.
2. Determine versions:
   - PHP: `config.platform.php` or `require.php`
   - PHPUnit: `require-dev.phpunit/phpunit` or `require-dev.symfony/phpunit-bridge`
   - Symfony: `require.symfony/framework-bundle` or `require.symfony/symfony`
3. Determine commands:
   - Prefer Composer scripts from `composer.json` (e.g. `test`, `phpunit`, `phpstan`, `csfixer`).
   - If there is no script, call the binaries directly (`vendor/bin/...` or `./bin/phpunit`).
4. If you need automation, run `scripts/detect_versions.py` in the project directory.
5. When versions are unclear, check `references/compatibility.md`.

### 2) Validate whether a test is needed

Do not write a test if:
- The change is purely cosmetic (formatting, comments, renames without behavior change).
- An existing test already covers the new behavior.
- The change affects only config/CI with no runtime impact.

Always write a test if:
- You change business logic or edge cases.
- You fix a bug with a reproduction.
- You add new functionality or an API contract.

### 3) Choose the test type

- **Unit**: pure logic, no DB/HTTP/IO; stubs/mocks, fast.
- **Integration**: collaboration across multiple classes/services, using the container, DB, cache.
- **Functional**: HTTP/CLI interaction, verifying responses and routing/security config.

If you're unsure, pick the lowest level that realistically verifies the required behavior.

### 4) Write the test for the detected versions

- Stick to syntax compatible with the detected PHPUnit version.
- In Symfony, use the appropriate base classes (e.g. `KernelTestCase`, `WebTestCase`).
- Keep tests short and unambiguous; one reason to fail per test.

### 5) Run in Docker (in order)

Always run via Docker using the `wodby/php:<version>` image detected from the project.

Example template:

```bash
docker run --rm -v "$PWD":/app -w /app wodby/php:7.4 <command>
```

**Order:**
1. PHPUnit
2. phpstan (only if PHPUnit is green)
3. php-cs-fixer (last)

If the project has Composer scripts, use them:

```bash
docker run --rm -v "$PWD":/app -w /app wodby/php:7.4 composer run phpunit
docker run --rm -v "$PWD":/app -w /app wodby/php:7.4 composer run phpstan
docker run --rm -v "$PWD":/app -w /app wodby/php:7.4 composer run csfixer
```

If there are no scripts:

```bash
docker run --rm -v "$PWD":/app -w /app wodby/php:7.4 vendor/bin/phpunit
docker run --rm -v "$PWD":/app -w /app wodby/php:7.4 vendor/bin/phpstan
docker run --rm -v "$PWD":/app -w /app wodby/php:7.4 vendor/bin/php-cs-fixer fix
```

## Resources

- `scripts/detect_versions.py` - detects PHP/PHPUnit/Symfony versions and suggests the Docker image.
- `references/compatibility.md` - compatibility hints when versions are unclear.
