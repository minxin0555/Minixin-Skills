# Minixin-Skills

Reusable Codex skills and supporting assets maintained for local AI workflows.

## Skills

| Skill | Version | Purpose |
| --- | --- | --- |
| `bio-figure` | `1.0` | Generate publication-grade biology and bioinformatics figures with reproducible code, export checks, and journal-style palettes. |
| `conda-env-selector` | `1.0` | Choose an appropriate conda environment before running Python code that depends on third-party packages. |

## Repository Layout

```text
.
├── bio-figure/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/
├── conda-env-selector/
│   └── SKILL.md
├── conda-env-selector-workspace/
└── _backup/
```

## Skill Format

Each skill lives in its own directory and uses `SKILL.md` as the entry point. The frontmatter declares the skill name, description, and version:

```yaml
---
name: example-skill
description: Short trigger and usage description.
version: "1.0"
---
```

Supporting materials such as references, scripts, assets, and evaluation files should stay inside the relevant skill or workspace directory.

## Versioning

Versions are tracked in `SKILL.md`.

- Minor updates increment the decimal version, for example `1.0` to `1.1`.
- Major rewrites move to the next major version, for example `1.7` to `2.0`.
- If a skill also has `meta.json`, its version should match `SKILL.md`.

## Backups

Version snapshots are stored under `_backup/<skill-name>/<skill-name>_v<version>/`.

Each backup snapshot should represent the completed version of that skill and include a `CHANGELOG.md` when update details are known.
