# Minixin-Skills

This repository collects public Codex skills maintained for repeatable local AI workflows. Each skill is a self-contained directory with a `SKILL.md` entry point and any supporting references or scripts it needs.

## Public Skills

### `bio-figure`

Publication-grade single-figure generation for biology and bioinformatics work.

Use it for common scientific plots such as volcano plots, DEG heatmaps, UMAP/PCA/t-SNE, Kaplan-Meier curves, ROC/PR curves, GO/KEGG/GSEA enrichment plots, Manhattan/QQ plots, correlation matrices, box/violin plots with significance, MA plots, and forest plots.

The skill emphasizes:

- one figure supporting one clear conclusion
- statistic-integrity checks
- reproducible plotting code
- PDF and high-resolution PNG export
- journal-style and colorblind-aware palettes

### `conda-env-selector`

A conda environment selection workflow for running Python code safely.

Use it before executing Python scripts, notebooks, apps, or analysis code that depends on third-party packages. It helps decide whether to use a project-specific environment, a shared general environment, or a newly created environment, while avoiding accidental installs into `base`.

The skill is especially useful for:

- running Python projects with dependencies
- handling `ModuleNotFoundError` or `ImportError`
- deciding where to install missing packages
- keeping project environments isolated and reproducible

## Directory Layout

```text
.
├── bio-figure/
│   ├── SKILL.md
│   ├── references/
│   └── scripts/
├── conda-env-selector/
│   └── SKILL.md
└── _backup/
```

## Skill Format

Each skill uses `SKILL.md` as its entry point. The frontmatter declares the skill name, trigger description, and version:

```yaml
---
name: example-skill
description: Short trigger and usage description.
version: "1.0"
---
```

Supporting materials such as references, scripts, and assets should stay inside the relevant skill directory.

## Versioning

Versions are tracked in `SKILL.md`.

- Minor updates increment the decimal version, for example `1.0` to `1.1`.
- Major rewrites move to the next major version, for example `1.7` to `2.0`.
- If a skill also has `meta.json`, its version should match `SKILL.md`.

## Backups

Version snapshots are stored under `_backup/<skill-name>/<skill-name>_v<version>/`.

Each backup snapshot should represent the completed version of that skill and include a `CHANGELOG.md` when update details are known.
