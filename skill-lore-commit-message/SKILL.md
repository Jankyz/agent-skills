---
name: skill-lore-commit-message
description: Create, validate, and write git commit messages in Lore protocol format with the `lore-protocol` CLI. Use when Codex needs to install Lore CLI, initialize `.lore/config.toml`, turn staged changes into a Lore-enriched commit, express decision context with Lore trailers, or validate that a commit complies with the Lore protocol after writing it.
---

# Lore Commit Message

## Overview

Use this skill to produce Lore-enriched commits that capture why a change exists, not just what changed. Prefer the JSON-to-`lore commit` flow because it is deterministic and aligns with the upstream agent workflow.

## Quick Start

1. Ensure the CLI exists:
   - `./scripts/install_lore_protocol.sh --dev`
   - `./scripts/install_lore_protocol.sh --global`
2. Ensure the repository is Lore-enabled:
   - `./scripts/ensure_lore_repo.sh`
3. Inspect staged work and gather decision context:
   - why this change exists
   - active constraints
   - rejected approaches
   - verification performed
   - known verification gaps
4. Draft or write the commit with structured JSON:

```bash
./scripts/write_lore_commit.py \
  --intent "Prevent duplicate job scheduling during retries" \
  --body "Retry attempts were enqueuing the same work twice under load." \
  --body "Gate rescheduling behind the persisted retry state instead." \
  --constraint "Must preserve at-least-once processing semantics" \
  --rejected "In-memory dedupe map | breaks across worker restarts" \
  --confidence high \
  --scope-risk narrow \
  --reversibility clean \
  --tested "Retry integration test with duplicate delivery" \
  --not-tested "Multi-node retry storm in production topology" \
  --print-json
```

5. Write the commit through Lore:

```bash
./scripts/write_lore_commit.py \
  --intent "Prevent duplicate job scheduling during retries" \
  --body-file /tmp/lore-body.txt \
  --constraint "Must preserve at-least-once processing semantics" \
  --rejected "In-memory dedupe map | breaks across worker restarts" \
  --confidence high \
  --scope-risk narrow \
  --reversibility clean \
  --tested "Retry integration test with duplicate delivery" \
  --not-tested "Multi-node retry storm in production topology" \
  --commit
```

## Workflow

### 1. Inspect the repository state

- Prefer staged changes over raw working tree noise:
  - `git diff --cached --stat`
  - `git diff --cached`
- Read recent Lore history when the repo already uses Lore:
  - `lore log --limit 5`
  - `lore constraints <path> --json`
  - `lore rejected <path> --json`
  - `lore directives <path> --json`

### 2. Convert the change into decision context

- Write the intent line as the reason for the change, not a diff summary.
- Keep the body short and narrative. Explain the tradeoff or failure mode that forced the change.
- Add trailers only when they express durable knowledge that future modifiers should see again.
- Use `Not-tested` instead of inventing confidence or test evidence.

### 3. Prefer structured JSON over interactive mode

Lore supports interactive mode, but agent workflows should prefer JSON on stdin. Use `scripts/write_lore_commit.py` to build that JSON, validate enums and trailer formats, and optionally pipe the payload into `lore commit`.

### 4. Validate after writing

- Run `lore validate HEAD^..HEAD` after the commit when the CLI is available.
- If the repo is newly Lore-enabled, inspect `.lore/config.toml` before assuming trailer requirements.
- If validation fails, fix the message and recommit instead of leaving a partial Lore adoption behind.

## Lore Drafting Rules

- Use the first line for intent, not taxonomy. Avoid messages such as `refactor: clean up utils`.
- Keep the body focused on the decision, tradeoff, or bug trigger.
- Format `Rejected` as `alternative | reason`.
- Use only the standard enums from the Lore CLI:
  - `Confidence`: `low`, `medium`, `high`
  - `Scope-risk`: `narrow`, `moderate`, `wide`
  - `Reversibility`: `clean`, `migration-needed`, `irreversible`
- Use 8-character hex Lore IDs for `Supersedes`, `Depends-on`, and `Related`.
- Keep `Directive` for forward-looking warnings, not generic reminders.

## Resources

### scripts/

- `scripts/install_lore_protocol.sh`: install `lore-protocol` globally or as a repo dev dependency.
- `scripts/ensure_lore_repo.sh`: initialize `.lore/config.toml` with the available Lore binary.
- `scripts/write_lore_commit.py`: validate a Lore payload, print JSON, write the payload to a file, or call `lore commit`.

### references/

- `references/lore-cli-and-paper.md`: condensed guidance from the Lore paper and upstream CLI README. Read this when you need the trailer vocabulary, installation commands, or the reasoning behind the protocol.
