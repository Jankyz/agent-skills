# agent-skills

This repository contains Codex skills (each skill is a folder with a `SKILL.md` entrypoint and optional `scripts/`, `references/`, etc.).

## Skills tree

```text
.
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