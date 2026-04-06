# Repository Instructions

This repository stores reusable Codex skills. Treat each top-level `skill-*` directory as an independent deliverable that can be copied into `~/.codex/skills`.

## Scope

These instructions apply to the entire repository.

## Skill Layout

- Name new skill directories with the `skill-` prefix.
- Every skill directory must contain a `SKILL.md` entrypoint.
- Add `agents/openai.yaml` for UI metadata when the skill should appear cleanly in skill lists.
- Add `scripts/`, `references/`, or `assets/` only when they are actually needed.
- Keep skill instructions concise; move detailed material into `references/`.

## Repository Conventions

- Update `README.md` whenever a skill is added, removed, or materially changed.
- Keep the README skill tree in sync with the committed directory structure.
- Do not commit local runtime artifacts such as `.omx/`, `__pycache__/`, `.DS_Store`, or generated logs.
- Prefer ASCII in committed files unless the file already requires another charset.

## Validation

- Run lightweight verification for every change:
  - syntax checks for added scripts
  - a direct smoke test for helper scripts when practical
  - `git diff` review for `README.md` and skill metadata
- If a provided validation helper is unavailable in the environment, use an equivalent local check and report the gap.

## Commits

- Follow the repository Lore commit protocol from the top-level operating contract.
- Write the first line as intent, not a file-change summary.
- Record real constraints, rejected options, and verification gaps instead of generic trailers.
