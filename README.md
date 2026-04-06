# agent-skills

This repository contains Codex skills (each skill is a folder with a `SKILL.md` entrypoint and optional `scripts/`, `references/`, etc.).

## Available skills

- `skill-lore-commit-message`: install and use the `lore-protocol` CLI to draft, validate, and write Lore-format git commits with structured trailers.
- `skill-php-behat-tests`: write, extend, debug, and run Behat scenarios in PHP/Symfony projects.
- `skill-php-symfony-phpunit-tests`: detect PHP/Symfony/PHPUnit compatibility and help maintain PHPUnit test suites in Symfony projects.

## Skills tree

```text
.
├── skill-lore-commit-message
│   ├── SKILL.md
│   ├── agents
│   │   └── openai.yaml
│   ├── references
│   │   └── lore-cli-and-paper.md
│   └── scripts
│       ├── ensure_lore_repo.sh
│       ├── install_lore_protocol.sh
│       └── write_lore_commit.py
├── skill-php-behat-tests
│   ├── SKILL.md
│   ├── agents
│   │   └── openai.yaml
│   └── scripts
│       ├── format_feature_step_alignment.py
│       └── suggest_behat_docker_cmd.sh
└── skill-php-symfony-phpunit-tests
    ├── SKILL.md
    ├── references
    │   └── compatibility.md
    └── scripts
        └── detect_versions.py
```

...more skills to come!
