---
name: symfony-phpunit-tests
description: Write and run Symfony tests with PHPUnit in Docker. Use when adding or updating tests in Symfony/PHP projects, deciding test type (unit/integration/functional), detecting PHP/PHPUnit/Symfony versions from composer.json/lock, and running phpunit then phpstan then cs-fixer in order.
---

# Symfony Phpunit Tests

## Overview

Wykonuj testy w projektach Symfony, dobieraj typ testu i skladnie pod wersje PHP/PHPUnit,
uruchamiaj je przez Docker, a potem uruchamiaj phpstan i cs-fixer w ustalonej kolejnosci.

## Workflow

### 1) Rozpoznaj wersje i tooling

1. Otworz `composer.json` i `composer.lock`.
2. Ustal wersje:
   - PHP: `config.platform.php` lub `require.php`
   - PHPUnit: `require-dev.phpunit/phpunit` lub `require-dev.symfony/phpunit-bridge`
   - Symfony: `require.symfony/framework-bundle` lub `require.symfony/symfony`
3. Ustal komendy:
   - Preferuj skrypty z `composer.json` (np. `test`, `phpunit`, `phpstan`, `csfixer`).
   - Jesli brak skryptu, uzyj bezposrednio binarek `vendor/bin/...` lub `./bin/phpunit`.
4. Jesli potrzebujesz automatu, uruchom `scripts/detect_versions.py` w katalogu projektu.
5. Gdy wersje sa niejasne, zajrzyj do `references/compatibility.md`.

### 2) Zweryfikuj czy test jest potrzebny

Nie pisz testu, jesli:
- Zmiana jest tylko kosmetyczna (formatowanie, komentarze, nazwy bez zmiany zachowania).
- Istniejacy test juz pokrywa nowe zachowanie.
- Zmiana dotyczy tylko konfiguracji/CI bez wplywu na runtime.

Zawsze pisz test, jesli:
- Zmieniasz logike biznesowa lub warunki brzegowe.
- Naprawiasz buga z reprodukcja.
- Dodajesz nowa funkcjonalnosc lub kontrakt API.

### 3) Dobierz typ testu

- **Jednostkowy**: czysta logika, bez bazy/HTTP/IO; stuby/moki, szybki.
- **Integracyjny**: wspolpraca kilku klas/uslug, uzycie kontenera, db, cache.
- **Funkcjonalny**: interakcja HTTP/CLI, sprawdzanie odpowiedzi i konfiguracji routing/security.

Jesli nie masz pewnosci, wybierz najnizszy poziom, ktory realnie weryfikuje wymagane zachowanie.

### 4) Napisz test pod wersje

- Trzymaj sie skladni zgodnej z wykrytym PHPUnit.
- W Symfony uzywaj odpowiednich klas bazowych (np. `KernelTestCase`, `WebTestCase`).
- Trzymaj testy krotkie i jednoznaczne; jeden powod porazki na test.

### 5) Uruchom w Dockerze (w kolejnosci)

Zawsze uruchamiaj przez Docker z obrazem `wodby/php:<wersja>` wykrytym z projektu.

Przykladowy szablon:

```bash
docker run --rm -v "$PWD":/app -w /app wodby/php:7.4 <komenda>
```

**Kolejnosc:**
1. PHPUnit
2. phpstan (tylko jesli PHPUnit zielony)
3. php-cs-fixer (na koniec)

Jesli projekt ma skrypty Composer, uzyj ich:

```bash
docker run --rm -v "$PWD":/app -w /app wodby/php:7.4 composer run phpunit
docker run --rm -v "$PWD":/app -w /app wodby/php:7.4 composer run phpstan
docker run --rm -v "$PWD":/app -w /app wodby/php:7.4 composer run csfixer
```

Jesli nie ma skryptow:

```bash
docker run --rm -v "$PWD":/app -w /app wodby/php:7.4 vendor/bin/phpunit
docker run --rm -v "$PWD":/app -w /app wodby/php:7.4 vendor/bin/phpstan
docker run --rm -v "$PWD":/app -w /app wodby/php:7.4 vendor/bin/php-cs-fixer fix
```

## Resources

- `scripts/detect_versions.py` - wykrywa wersje PHP/PHPUnit/Symfony i podpowiada obraz Dockera.
- `references/compatibility.md` - wskazowki kompatybilnosci, gdy wersje sa niejasne.
