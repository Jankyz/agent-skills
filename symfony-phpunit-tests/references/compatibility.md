# Compatibility Notes (Symfony/PHPUnit/PHP)

Use these notes only as guidance. Always prefer the constraints from `composer.json` and
locked versions from `composer.lock` when deciding syntax or tooling.

## PHP vs PHPUnit (typical support)

- PHP 7.4: usually PHPUnit 9.5.x (newer majors often require PHP 8+)
- PHP 8.0: usually PHPUnit 9.5.x
- PHP 8.1+: PHPUnit 10.x is commonly available
- PHP 8.2+: PHPUnit 10.x/11.x may be available depending on constraints

## Symfony and PHPUnit runner

- If `symfony/phpunit-bridge` is present, prefer running `./bin/phpunit` (or the Composer
  script that calls it). It pins a compatible PHPUnit version.
- If `phpunit/phpunit` is present, prefer `vendor/bin/phpunit`.

## Syntax hints to adjust by PHPUnit version

- If PHPUnit is older, avoid newer attribute-based annotations and stick to classic docblock
  annotations and method names available in that major.
- If PHPUnit is newer, be mindful of deprecations in assertions and lifecycle hooks; check
  release notes for the exact major locked in `composer.lock`.
