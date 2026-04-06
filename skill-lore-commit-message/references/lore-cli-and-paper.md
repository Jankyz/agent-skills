# Lore CLI And Paper

## Core Idea

Lore treats a git commit message as a machine-readable decision record instead of a label for a diff. The paper calls the missing rationale behind code changes the "Decision Shadow": the constraints, rejected alternatives, and future-facing warnings that usually disappear once the diff lands.

Read the upstream sources when you need more detail:

- Repository: https://github.com/Ian-stetsenko/lore-protocol
- Paper: https://arxiv.org/abs/2603.15566

## Why Use Lore

- Preserve implementation-level rationale without adding extra infrastructure.
- Keep decision context atomically bound to the commit that introduced the change.
- Make the history queryable by humans and agents through a CLI instead of custom parsing.

The paper argues that this is lighter than ADRs or separate agent-memory systems because git already provides storage, distribution, and native trailer support.

## Commit Anatomy

Use three layers:

1. Intent line: explain why the change exists.
2. Body: explain the tradeoff, bug trigger, or design pressure in a few lines.
3. Trailers: encode stable, machine-readable decision context.

The paper and README both stress that the intent line should describe the reason for the change, not a summary of file edits.

## Standard Trailer Vocabulary

Supported by the upstream CLI and paper:

- `Lore-id`: exactly one 8-character hex identifier
- `Constraint`: active requirement that future work must still respect
- `Rejected`: rejected alternative in `alternative | reason` format
- `Confidence`: `low`, `medium`, `high`
- `Scope-risk`: `narrow`, `moderate`, `wide`
- `Reversibility`: `clean`, `migration-needed`, `irreversible`
- `Directive`: forward-looking warning for future modifiers
- `Tested`: what was verified
- `Not-tested`: what remains unverified
- `Supersedes`: previous Lore atom replaced by this one
- `Depends-on`: Lore atom that this decision relies on
- `Related`: informational link to another Lore atom

## Upstream Installation And Setup

The README documents:

```bash
npm install -g lore-protocol
```

Requirements:

- Node.js 18 or newer

Repository setup:

```bash
lore init
```

This creates `.lore/config.toml`.

## Upstream Commit Flow

The upstream CLI supports three authoring paths:

### Interactive

```bash
lore commit -i
```

### Direct flags

```bash
lore commit \
  --intent "refactor: extract validation into dedicated service" \
  --constraint "must remain synchronous -- called in hot path" \
  --rejected "class-validator decorators | too much magic for simple checks" \
  --confidence high \
  --scope-risk narrow \
  --tested "unit tests for all validation rules"
```

### JSON on stdin

This is the best path for agents:

```bash
echo '{
  "intent": "fix: handle expired sessions gracefully",
  "body": "Previously threw 500 on expired session. Now returns 401 with clear message.",
  "trailers": {
    "Constraint": ["must not log session tokens"],
    "Rejected": ["silent redirect to login | breaks API clients"],
    "Confidence": "high",
    "Scope-risk": "narrow",
    "Tested": ["expired session returns 401", "valid session still works"],
    "Not-tested": ["concurrent session expiry race condition"]
  }
}' | lore commit
```

## Agent Workflow From The Paper

The paper describes this consumption loop:

1. Discover `.lore/config.toml` or Lore-formatted commits.
2. Query context before editing:
   - `lore context <path>`
   - `lore constraints <path>`
   - `lore rejected <path>`
   - `lore directives <path>`
3. Avoid repeating rejected approaches.
4. Write the new decision as a Lore-enriched commit.

The paper positions Lore as permanent project memory across sessions, while tools such as Git Context Controller handle a single agent's temporary working memory.

## Validation

Use the CLI to check compliance:

```bash
lore validate HEAD^..HEAD
```

Other useful commands:

- `lore log`
- `lore context <target>`
- `lore why <file:line>`
- `lore search`
- `lore doctor`

## Practical Drafting Heuristics

- Prefer one logical decision per commit.
- Promote only durable information to trailers.
- Avoid fabricating `Tested` or `Confidence`.
- Record rejected approaches when they would otherwise be re-tried by a future agent.
- Add `Directive` only when violating it would likely create a regression.
