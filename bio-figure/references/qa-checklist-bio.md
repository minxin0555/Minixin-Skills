# QA checklist — before delivering any figure

Run through these in order. A figure is not done until every box is ticked (or explicitly waived in the report with a reason).

## 1. Conclusion

- [ ] There is exactly one falsifiable conclusion attached to this figure.
- [ ] Every numeric value in the conclusion is either `[computed]` by this skill in this run or `[user-provided]` from a result table.
- [ ] If no statistic was computed, the conclusion is phrased as a question and tagged `[question-form, no stats]`.
- [ ] The figure visibly supports the conclusion at a glance — a colleague glancing at the figure could state the conclusion without reading the caption.

## 2. Chart and statistics

- [ ] The chart type is from `chart-types-bio.md` (or has an explicit reason to deviate).
- [ ] If significance marks (`*`, p-values, brackets) appear, the test used is named in the figure / caption / report.
- [ ] Multiple-comparison correction is applied (BH / Bonferroni) when there are ≥ 3 groups, and the method is named.
- [ ] `n` and the error-bar definition (SD / SEM / 95 % CI / bootstrap band) are stated where applicable.

## 3. Axes and labels

- [ ] Both axes have a label including units.
- [ ] Tick numbers are readable (5–8 pt) and not crowded.
- [ ] Scale handling: log / broken-axis / normalised is applied when the data spans orders of magnitude, and the choice is documented.
- [ ] Dual y-axes are used only when the two quantities are conceptually paired; otherwise small multiples were used.

## 4. Palette

- [ ] Default qualitative palette is colorblind-safe (Okabe-Ito), **or** a journal palette was chosen and its non-colorblind-safe status is recorded in the report.
- [ ] Diverging palette is centred on 0 with a faint-grey midpoint (not pure white) on a white background.
- [ ] Sequential palette is monotonic in luminance (no perceptual reversal).
- [ ] If the palette was changed at user request, swatch PNG was shown and the chosen scheme is recorded.

## 5. Legend and labels

- [ ] Legend is placed outside the axes by default, or the in-axes pixel-overlap check passed (`export-bio.md` §4.1).
- [ ] Text labels (genes / clusters / variables) do not overlap each other or the data. `adjustText` or fallback de-overlap was used; only top-N labelled.

## 6. Typography

- [ ] Font is Arial (or recorded fallback to Helvetica / DejaVu Sans).
- [ ] All text is in English.
- [ ] Body font 7 pt; ticks 5–6 pt; legend 6 pt; title ≤ 8 pt.
- [ ] PDF `fonttype = 42` (TrueType).

## 7. Export and archive

- [ ] Both `<stem>.pdf` and `<stem>.png` (≥ 600 dpi) were saved.
- [ ] Files live under `<project root>/AI-figure/run-<timestamp>/figures/`.
- [ ] The plotting script lives under `code/` and was the file that actually drew the figure (not reconstructed after the fact).
- [ ] Filename stems are descriptive (e.g. `volcano_TvsC`), not `figureN`.
- [ ] Existing files were not silently overwritten — the run subdirectory uniquifies output.

## 8. Reproducibility

- [ ] The script in `code/<stem>.py` can be re-run with the same data path and produce the same figure.
- [ ] Random seeds are fixed wherever stochastic computations are involved (PCA jitter is deterministic; UMAP / t-SNE seeds came from the user).
- [ ] Dependencies used in the script are listed at the top of the file.

## 9. Report integration

- [ ] `report.md` has a section for this figure with: conclusion + source tag, chart rationale, palette choice, statistics, overlap check status, file paths.
- [ ] If the palette was non-colorblind-safe, the warning is in the report.
- [ ] If a font fallback occurred, it is in the report.
