---
name: bio-figure
description: Publication-grade single-figure generator for biology / bioinformatics. Use when the user wants a volcano plot, DEG heatmap, UMAP / PCA / t-SNE, Kaplan-Meier survival curve, ROC / PR, GO / KEGG / GSEA enrichment, Manhattan / QQ, correlation matrix, box / violin + significance, MA plot, forest plot — or any "SCI figure / publication figure / Nature-style plot" of bio data. Also use when the user asks "what should I plot from this data" (recommendation) or wants a batch of figures from a dataset. Four working modes (0 direct-draw / A recommend-with-data / B recommend-without-data / C batch-direct), one-sentence conclusion gate with statistic-integrity guardrails, journal palettes (NPG / AAAS / NEJM / Lancet / Okabe-Ito) + same-hue sequential / diverging, default Python (matplotlib / seaborn / scanpy), English Arial labels, PDF + ≥600dpi PNG exported into project-root AI-figure/run-<timestamp>/ with a fully reproducible code/ folder and report.md. Light analyses (t-test / Mann-Whitney / ANOVA / PCA / correlation / KM + log-rank / ROC) are computed internally; heavy pipelines (DESeq2 / full single-cell QC→clustering / variant calling) require the user's pre-computed result table. Skip for: generic non-bio figures, multi-panel layout / composite Fig 1 a-f assembly, interactive / web plots (plotly, altair), or actually running heavy analysis pipelines.
version: "1.0"
---

# bio-figure — publication-grade bio figure generator

Turn `(data + one-sentence conclusion)` into a single figure that can stand on its own in a paper: vector PDF + ≥600 dpi PNG, English Arial, journal palette, colorblind-safe by default, archived under `AI-figure/`.

## Core principles

1. **One figure, one conclusion.** Every figure must visually support a falsifiable claim. No claim → no figure starts.
2. **Statistic-integrity guardrail.** Any number in the conclusion (p, FDR, HR, log2FC, r, AUC…) must come from either (a) a computation this skill actually ran, or (b) a result table the user provided. **Never invent statistics.** If nothing was computed, the conclusion must be phrased as a *question* the figure answers, not a claim with numbers.
3. **Light analysis + figure only.** This skill runs single-function-level statistics and dimensionality reduction (t-test, Mann-Whitney, ANOVA, PCA, correlation, KM + log-rank, ROC / PR). It does **not** run heavy pipelines (DESeq2 / edgeR / full scRNA-seq QC→clustering / variant calling). Those must come in as a pre-computed result table.
4. **Python by default.** matplotlib / seaborn / scanpy. Only switch to a light R / ggplot2 branch if the user explicitly asks for R.
5. **Conclusion → chart → palette → export → QA.** Always in this order. The conclusion drives every later choice.
6. **Self-contained.** This skill's files do not depend on any other skill; if other compatible skills are present at runtime they may cooperate naturally, but the file content here never names or relies on them.

---

## Quick start (mode 0, the fastest path)

User: *"Plot a volcano from `deg.csv`."*

1. Read `deg.csv` with pandas; auto-detect `gene` / `log2FC` / `pvalue` (or `padj`) columns and **echo the mapping back in one line** for the user to confirm/correct *only* if any key column is ambiguous.
2. Apply default thresholds (`|log2FC| ≥ 1`, `padj < 0.05`) unless the user said otherwise.
3. Pick palette by §6 (two-class default: blue / orange Okabe-Ito; or NPG red / blue if user wants journal look — then warn it is not colorblind-safe).
4. Write the plotting script to `AI-figure/run-<timestamp>/code/volcano_<tag>.py` first, **then execute it** to produce the figure (so `code/` is always the true source).
5. Save `volcano_<tag>.pdf` and `volcano_<tag>.png` (600 dpi) to `AI-figure/run-<timestamp>/figures/`.
6. Run the overlap self-check (legend + text labels, see `references/export-bio.md`).
7. Attach a one-sentence conclusion that obeys the integrity guardrail (see §4).

Do **not** block on conclusion confirmation in mode 0 — auto-draft it and proceed.

---

## 1. Scope, data inputs, dependencies

### 1.1 What this skill computes vs. what the user must provide

| Category | bio-figure can compute | User must provide result table |
|---|---|---|
| Differential expression | — | DEG table (`gene`, `log2FC`, `pvalue` / `padj`) |
| Group comparison | t-test / Mann-Whitney / ANOVA / Kruskal, mean ± SD/SEM | — |
| Dimensionality reduction | PCA (from numeric matrix), correlation matrix | UMAP / t-SNE coordinates (or pre-embedded `.h5ad`) |
| Survival | KM curve + log-rank (from `time` / `event` table; uses `lifelines`) | — |
| Classification performance | ROC / PR + AUC (from `score` / `label`; uses `scikit-learn`) | — |
| Enrichment | Bubble plot from an enrichment result table | GO / KEGG / GSEA enrichment results |
| GWAS | Manhattan / QQ (from `chr` / `pos` / `p` table) | — |

**Rule of thumb:** if it is a one-line stats call, compute it and use the result in the conclusion. If it is a modeling pipeline, ask the user for the result table — do not fake or skip.

### 1.2 Supported / unsupported data formats

- **Supported (Python-native):** `.csv` / `.tsv` / `.txt`, `.xlsx` (`openpyxl`), `.h5ad` (`scanpy / anndata`), `.mtx` + 10x dir, `.parquet`.
- **Unsupported in Python:** `.rds` / `.RData`. **Do not fail silently** — tell the user to either re-export from R as CSV/TSV, or invoke the light R branch.
- **Column mapping:** after reading the table, infer the key columns (e.g. log2FC, p-value, gene name, group) and **echo them back in a single line** before plotting. Never guess columns silently.

### 1.3 Dependencies and environment

- **Base:** `matplotlib`, `numpy`, `pandas`, `scipy`, `seaborn`.
- **On demand:** KM → `lifelines`; ROC / PR → `scikit-learn`; single-cell read → `scanpy` / `anndata`; Excel → `openpyxl`; label de-overlap (optional) → `adjustText`.
- **Environment policy:** run in a Python env that already has the packages above (prefer the project's existing env). If none, use / create a general-purpose env. **Never install into `base`.** If another env-management skill is present at runtime, it may pick the env; this skill's logic still works without it.
- **Missing-package handling:** check required imports **before** plotting. If anything is missing, **stop and report exactly what is missing plus the install command.** Do not silently downgrade to a simpler chart, do not crash mid-plot.

---

## 2. Four working modes

After the user's request, decide the mode by `(does the user name a specific chart?) × (is data given?)`:

### Mode 0 — Direct single figure (fastest)
**Trigger:** the user named a specific chart ("plot a volcano", "draw a KM curve").
**Flow:** read data → confirm columns *only if ambiguous* → pick palette per §6 (or honor user's request) → write script → execute → export → overlap self-check → auto-attach a one-sentence conclusion (statistic-integrity guardrail applies).
**Do not block** on conclusion confirmation in this mode.

### Mode A — Recommend, with data
**Trigger:** the user gave data but asked for a recommendation ("what should I plot from `expr.csv`?").
**Flow:** read data → identify data type and statistical structure → draft the conclusion → propose 1–2 chart types (with reason + axis / scale / palette plan) → **ask the user which one** → plot → export → overlap self-check.

### Mode B — Recommend, without data (exploratory)
**Trigger:** no data path given, or "what could I plot in this project?".
**Flow:** scan project for tabular / `.h5ad` / matrix files → produce an **opportunity list** of the form `{available file → chart type → conclusion it can support (guardrailed phrasing) → reason}` → **wait for user pick.** Do not plot directly.

### Mode C — Batch direct output
**Trigger:** "plot everything you can from this dataset" / "give me a batch".
**Flow:** reuse the recognition + recommendation from A/B → **do not ask**, plot all recommended figures. Cap: **≤5 → plot all; >5 → list them first and let the user trim before plotting.** After all figures are done, write a `report.md` (see §6).

### Ambiguity fallback
If the user's intent is vague ("how do I visualize this?"), default to a recommendation mode (A if data is given, else B) — do **not** silently jump to batch.

All four modes share the same underlying components (data recognition / conclusion gate / chart library / palette / export / QA); they differ only in interaction and whether they batch.

---

## 3. Conclusion gate + integrity guardrail

See `references/conclusion-gate.md` for full text.

- A conclusion is a **falsifiable declarative sentence**, not a topic.
  - ✓ "Gene X is expressed significantly higher in group A than in group B (p < 0.01)."
  - ✗ "Show the difference between two groups."
- If the user did not give one, the AI drafts 1–2 candidates and lets the user pick / amend with one tap.
- **Integrity guardrail (hard rule).** Any number in the conclusion (p, FDR, HR, log2FC, r, AUC…) must have actually been computed by this skill *or* must come from a user-provided result table.
  - If nothing has been computed, **do not write a number.** Write a question-shaped conclusion: "This figure examines whether X and Y are associated."
  - In the report (§6) tag every conclusion with its source: `[computed]` / `[user-provided]` / `[question-form, no stats]`.

---

## 4. Chart library, palette, export, QA

These are spelled out in the `references/` directory; load the relevant file when the mode reaches that step.

| Step | File |
|---|---|
| Pick chart type | `references/chart-types-bio.md` |
| Read data / map columns / handle deps | `references/data-input-bio.md` |
| Pick palette | `references/color-system-bio.md` + `scripts/palette.py` |
| Conclusion + guardrail | `references/conclusion-gate.md` |
| Style / size / DPI / overlap self-check | `references/export-bio.md` |
| Final acceptance | `references/qa-checklist-bio.md` |

### Defaults at a glance

- **Language / font:** English, Arial (fallback Helvetica / DejaVu Sans).
- **Font size:** 7 pt body; 5–8 pt for tick / legend.
- **Spines:** top + right off, `axes.linewidth = 0.8`.
- **PDF font type:** 42 (TrueType, editable in Illustrator). SVG `fonttype = "none"`.
- **Width:** single column ≈ 85 mm; double column ≈ 170 mm.
- **Export:** PDF (vector) + PNG at ≥600 dpi.
- **Palette default:**
  - 1-series → journal first colour (NPG `#E64B35`, NEJM `#BC3C29`, …) per §`color-system-bio.md`.
  - 2-class → blue / orange (Okabe-Ito, colorblind-safe). Switch to NPG red / blue if the user wants journal look — and warn it is not colorblind-safe.
  - ≥3 unordered classes → Okabe-Ito by default; switch to NPG / AAAS only on request, with a colorblind-safety warning.
  - Continuous → same-hue sequential (HCL: fix hue, vary chroma↓ / luminance↑) via `palette.py sequential`.
  - Diverging → blue ↔ light-grey centre ↔ red (do not use pure white as centre on a white background; use a faint grey).

---

## 5. Output layout

Default to `<project root>/AI-figure/`. Project root is `git rev-parse --show-toplevel` if in a git repo, else the current working directory. Each run lives in its own timestamped subdirectory — never overwrite a previous run.

```
<project root>/AI-figure/
└── run-YYYYMMDD-HHMMSS/
    ├── figures/    # volcano_TvsC.pdf|.png, km_OS_subtype.pdf|.png …  (descriptive stems, not figure1/2/3)
    ├── code/       # one reproducible script per figure
    └── report.md   # mode C, also useful for A/B
```

**Reproducibility rule (§8.2 of the design doc):** write the plotting script into `code/` first, then *execute that script* to produce the figure. Never reconstruct `code/` after the fact — the file in `code/` must be the file that actually drew the figure.

If the user supplies an explicit path / filename, honour that instead.
If the target already exists and was not created by this skill, do not silently overwrite — surface it and ask.

### `report.md` template

```markdown
## Figure N — <chart type>
- Conclusion: <one sentence>  [source: computed / user-provided / question-form]
- Why this chart: <data ↔ chart fit>
- Palette: <which scheme and why>
- Statistics: <test / n / error bar definition>  (if applicable)
- Overlap check: passed / adjusted (<note>)
- Result: ![Figure N](figures/<stem>.png)
- Files: figures/<stem>.pdf|.png · Code: code/<stem>.py
```

---

## 6. Overlap self-check (mandatory before delivery)

Two checks every figure must pass; details in `references/export-bio.md`.

1. **Legend occlusion.** Default to placing the legend **outside** the axes (`bbox_to_anchor` to the right or bottom, and grow the canvas). If the user insists on inside-axes, sample the legend pixel region against the canvas and check for non-background drawn pixels (the bbox-intersection method overreports). If the categories are fixed and few, prefer direct in-figure annotation over a legend.
2. **Text-label overlap** (volcano gene labels, UMAP cluster labels). Use `adjustText` if installed, else a small repulsion routine. Only label top-N points; do not flood the figure.

Record the result in the report: `Overlap check: passed` or `adjusted (<what was changed>)`.

---

## 7. Statistic-annotation correctness

When plotting significance stars / brackets / p-values:

- Two groups: check normality and n → t-test vs Mann-Whitney. Do not default to t-test silently.
- Multiple groups: ANOVA / Kruskal, with **multiple-comparison correction** (BH / Bonferroni) clearly stated.
- Always print which test was used (in the figure caption / report); never write `*` without naming the test.
- If the right test is unclear, ask the user or fall back to a description-only chart (no significance marks, no fabricated numbers).

---

## 8. Light R branch (only if the user asks for R)

Trigger phrases: "use R", "ggplot2", "give me an R script".
Output: a minimal self-contained `.R` snippet using `ggplot2` (+ `ggpubr` / `survminer` only if essential), with the same conclusion gate, palette, and export rules (PDF + PNG ≥600 dpi, Arial, English).
Do not auto-switch to R; the Python path is the default for all other triggers.

---

## 9. Non-goals (explicit, to avoid scope creep)

- Multi-panel composite layout (Fig 1 a–f assembly) — this skill produces single figures. Compositing is the user's downstream job.
- Heavy analysis pipelines (DESeq2 / edgeR / full scRNA-seq QC→clustering / variant calling). Bring the result table.
- Interactive / web figures (plotly, altair, bokeh).
- Generic, non-biology infographics.

---

## 10. When to load

**Load when the user wants:**
- A biology / bioinformatics figure: volcano, MA, DEG heatmap, UMAP / PCA / t-SNE, KM survival, GO / KEGG / GSEA enrichment, Manhattan / QQ, correlation matrix, box / violin with significance, ROC / PR, forest, bubble enrichment.
- A "publication-grade" single figure (English Arial, vector PDF + high-DPI PNG) archived under `AI-figure/`.
- A "what should I plot from this data?" recommendation, with a conclusion-first workflow.

**Do not load for:**
- Generic non-bio figures.
- Multi-panel composite layout / poster assembly.
- Interactive / web figures.
- Running heavy analysis pipelines themselves.
