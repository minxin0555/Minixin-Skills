# Bio chart library

For each chart: **what conclusion it supports · axes · statistics · scale + palette guidance · Python implementation notes · required input columns · required dependencies**. Pick from this library first; do not invent flashy commercial-style charts.

Naming convention used below:
- *Required columns* are listed under field names that downstream code expects after the column-mapping confirmation (see `data-input-bio.md`).
- *Deps* lists packages **on top of** the base `matplotlib + numpy + pandas + scipy + seaborn`.

---

## I. Differential / comparison

### 1. Volcano plot
- **Conclusion shape:** "Gene X / a class of genes is up- (down-) regulated in condition A vs B, and statistically significant."
- **Axes:** x = `log2FoldChange`, y = `-log10(pvalue)` (or `-log10(padj)`).
- **Statistics:** thresholds — default `|log2FC| ≥ 1` and `padj < 0.05`; configurable.
- **Scale / palette:** symmetric x around 0; two-class palette (up = warm, down = cool, non-sig = grey). Default Okabe-Ito orange / blue + `#BFBFBF`.
- **Implementation:** scatter with three colour groups; label only top-N by combined rank (`-log10(padj) × |log2FC|`); use `adjustText` or manual repulsion (see `export-bio.md`).
- **Required columns:** `gene`, `log2FoldChange`, `pvalue` or `padj`.
- **Deps:** *(none beyond base)*; optional `adjustText`.

### 2. MA plot
- **Conclusion shape:** "Fold-change is concentrated at high (low) expression and significantly biased toward up- (down-) regulation."
- **Axes:** x = `log2(baseMean)` (or `A = (log2(A)+log2(B))/2`), y = `log2FC`.
- **Statistics:** same significance thresholds as volcano.
- **Palette:** sig vs non-sig two-class.
- **Implementation:** scatter; horizontal line at y = 0; mark significant points.
- **Required columns:** `gene`, `baseMean` (or both group means), `log2FoldChange`, `padj`.
- **Deps:** *(none beyond base)*.

### 3. Grouped bar / column with significance brackets
- **Conclusion shape:** "Group A is significantly higher / lower than group B (test = …, p = …)."
- **Axes:** x = categorical group; y = measured value.
- **Statistics:** two groups → t-test (normal) or Mann-Whitney; ≥3 → ANOVA / Kruskal + BH correction. **State the test used.**
- **Palette:** two-class or qualitative (Okabe-Ito).
- **Implementation:** bar = mean, error bar = SD or SEM (state which); jitter raw points on top if n ≤ 30.
- **Required columns:** long format `group`, `value`, (`replicate` optional).
- **Deps:** *(none beyond base)*.

### 4. Box / violin + jittered points
- **Conclusion shape:** "Distribution in A is shifted higher / has higher variance than B, p = …"
- **Axes:** x = group; y = value.
- **Statistics:** same as #3.
- **Palette:** two-class or qualitative.
- **Implementation:** seaborn `boxplot` + `stripplot` overlay, or `violinplot` with `inner='quartile'`; significance brackets via `matplotlib` lines + text.
- **Required columns:** `group`, `value`.
- **Deps:** *(none beyond base)*.

---

## II. Dimensionality reduction / clustering / matrix

### 5. PCA / UMAP / t-SNE scatter
- **Conclusion shape:** "Samples / cells cluster by `condition` along PC1 (or in UMAP space), suggesting `condition` is the dominant source of variance."
- **Axes:** PC1 / PC2 (with %variance), or UMAP1 / UMAP2.
- **Statistics:** PCA can be computed here (sklearn `PCA`). UMAP / t-SNE coordinates must be **pre-computed** by the user (or already in `.h5ad`).
- **Palette:** qualitative for ≤ 8 clusters (Okabe-Ito default); same-hue sequential if encoding a continuous covariate (e.g. pseudotime).
- **Implementation:** matplotlib scatter; cluster labels placed at cluster centroids (use `adjustText` to avoid overlap); legend off-axes.
- **Required columns:** `embedding_1`, `embedding_2`, `group` (or `cluster`); for PCA, a numeric matrix with samples as rows.
- **Deps:** `scikit-learn` for PCA; `scanpy` / `anndata` for `.h5ad`; optional `adjustText`.

### 6. Expression heatmap with clustering dendrogram
- **Conclusion shape:** "Selected genes form two co-expression blocks aligning with `condition`."
- **Axes:** rows = genes, columns = samples (or vice versa).
- **Statistics:** z-score per row before plotting (standard); state the standardisation.
- **Palette:** diverging blue → light grey → red (or purple ↔ green) with 0 centred. Cap colour scale at `±2.5` or symmetric quantile to avoid one outlier washing out the rest.
- **Implementation:** seaborn `clustermap` (computes dendrograms); column annotation bar for `condition`.
- **Required columns:** wide matrix `gene × sample`, plus a sample metadata table for the annotation bar.
- **Deps:** *(none beyond base)*.

### 7. Correlation matrix heatmap
- **Conclusion shape:** "Variables X and Y are strongly positively correlated (r = …, p = …); X and Z are uncorrelated."
- **Axes:** square matrix of variables.
- **Statistics:** Pearson / Spearman; compute via `scipy.stats`. State which.
- **Palette:** diverging, centred at 0; range `[-1, 1]`.
- **Implementation:** numeric annotation in cells if ≤ 12 variables; mask the upper triangle to reduce redundancy.
- **Required columns:** numeric matrix (samples × variables).
- **Deps:** *(none beyond base)*.

### 8. Manhattan plot (+ QQ)
- **Conclusion shape:** "Locus on chr X reaches genome-wide significance (p < 5×10⁻⁸) for trait Y."
- **Axes:** x = genomic position (chr-aware tick layout), y = `-log10(p)`.
- **Statistics:** none beyond per-SNP p-values provided.
- **Palette:** alternating two-tone by chromosome (e.g. `#3B4992` / `#A9A9A9`); highlight top loci in a third colour.
- **Implementation:** group by chromosome, cumulative offset; horizontal lines at `5e-8` and `1e-5`. QQ plot in a sibling figure.
- **Required columns:** `chr`, `pos`, `pvalue`, optional `snp_id`.
- **Deps:** *(none beyond base)*.

---

## III. Survival / clinical

### 9. Kaplan-Meier curve (+ risk table + log-rank)
- **Conclusion shape:** "Patients in subgroup A have significantly shorter OS than B (log-rank p = …, median OS = …)."
- **Axes:** x = time (months / days, state unit), y = survival probability `[0, 1]`.
- **Statistics:** `lifelines.KaplanMeierFitter` + `lifelines.statistics.logrank_test`.
- **Palette:** two-class (or up to 4-class qualitative).
- **Implementation:** plot KM curves with censor ticks; add a number-at-risk table below; place the log-rank p in the top-right of the axes.
- **Required columns:** `time`, `event` (0/1), `group`.
- **Deps:** `lifelines`.

### 10. Forest plot
- **Conclusion shape:** "Variable X is an independent risk factor (HR = …, 95% CI …, p = …)."
- **Axes:** x = effect size (HR or OR) on log scale; y = list of variables.
- **Statistics:** values come from the user's model output table.
- **Palette:** monochrome; reference line at HR = 1.
- **Implementation:** matplotlib errorbar (asymmetric on log scale); annotate HR + CI + p on the right margin.
- **Required columns:** `variable`, `estimate`, `ci_lower`, `ci_upper`, `pvalue`.
- **Deps:** *(none beyond base)*.

### 11. ROC / PR curve with AUC
- **Conclusion shape:** "Model M classifies condition C with AUROC = …, outperforming baseline."
- **Axes:** ROC — FPR vs TPR (diagonal reference); PR — recall vs precision.
- **Statistics:** `sklearn.metrics.roc_curve` / `precision_recall_curve` + `auc`.
- **Palette:** qualitative if comparing multiple models; otherwise single colour.
- **Implementation:** one line per model; legend = model + AUC.
- **Required columns:** `score`, `label` (binary); or one such pair per model.
- **Deps:** `scikit-learn`.

---

## IV. Enrichment / pathway

### 12. GO / KEGG enrichment bubble plot
- **Conclusion shape:** "DEGs are enriched for `pathway X` (padj = …, gene ratio = …)."
- **Axes:** x = `GeneRatio` or `-log10(padj)`; y = term (ordered by significance, truncate long names).
- **Statistics:** values from the enrichment result table (not recomputed here).
- **Palette:** dot colour = `padj` (sequential), dot size = gene count.
- **Implementation:** sort by significance; truncate term names ≥ 50 chars with ellipsis.
- **Required columns:** `term`, `pvalue` / `padj`, `gene_count`, `gene_ratio` (or `bg_ratio`).
- **Deps:** *(none beyond base)*.

### 13. GSEA running enrichment curve
- **Conclusion shape:** "Gene set S is significantly enriched at the top of the ranked list (NES = …, FDR = …)."
- **Axes:** top — running ES; middle — hit ticks; bottom — ranked metric.
- **Statistics:** values from the user's GSEA output.
- **Palette:** single-curve colour; hit ticks black.
- **Implementation:** three-panel stacked figure sharing x; annotate NES, p, FDR.
- **Required columns:** ranked gene list + per-gene running ES (or a GSEA output object).
- **Deps:** *(none beyond base)*; optionally `gseapy` for the underlying calculation.

### 14. Network / pathway graph
- **Conclusion shape:** "Hub gene X connects modules A and B."
- **Note:** this skill produces **only a static layout** if the user supplies node + edge tables with positions; for actual layout algorithms, defer to `networkx` and ask the user to confirm layout choice (spring, kamada-kawai).
- **Required columns:** `nodes` (`id`, attrs), `edges` (`source`, `target`, optional `weight`).
- **Deps:** `networkx`.

---

## V. Composition / trend / relation

### 15. Stacked / 100% stacked bar
- **Conclusion shape:** "Cell-type composition shifts toward type T in condition C."
- **Axes:** x = sample / condition; y = count or proportion.
- **Palette:** qualitative (Okabe-Ito if ≤ 8); never use rainbow.
- **Implementation:** sort categories by mean proportion; legend outside.
- **Required columns:** long format `sample`, `category`, `value`.

### 16. Scatter with fit + confidence band
- **Conclusion shape:** "Variable X correlates with Y (r = …, p = …, slope = …)."
- **Statistics:** Pearson / Spearman + linear regression (`scipy.stats.linregress` or `numpy.polyfit`); state which.
- **Palette:** points one colour, fit line + CI in a second colour.
- **Required columns:** `x`, `y`.

### 17. Bubble plot
- **Conclusion shape:** "Genes / pathways with high expression also have high significance."
- **Axes:** x, y, dot size = third dim, dot colour = fourth dim.
- **Required columns:** four numeric columns.

### 18. Line with confidence band
- **Conclusion shape:** "Variable V increases over time T in condition C."
- **Statistics:** mean + bootstrap / SD / SEM band — state which.
- **Required columns:** `time`, `value`, `group`, optional `replicate`.

### 19. Faceted grid (small multiples)
- **Conclusion shape:** "Pattern P holds across subsets S1, S2, S3."
- **Implementation:** seaborn `FacetGrid` / `relplot` / `catplot`; share axis scales unless contrast across facets is the point.

---

## Chart-selection constraints (apply always)

- Prefer this library; do not invent novelty chart types.
- Statistical rigour:
  - Multiple replicates → error bars / confidence band; state `n` and definition.
  - Two-group → choose test by normality (Shapiro / visual) and `n`; state the test.
  - Multi-group → ANOVA / Kruskal with BH or Bonferroni correction; state the method.
- Scale handling — pick one of three when data spans orders of magnitude:
  - Broken axis (sparingly), log axis, or normalisation.
- Long labels → rotate or use horizontal bars; do not let labels run into each other.
- Dual y-axes only when the two quantities are conceptually paired; otherwise use small multiples.
- One conclusion per figure. If two conclusions, two figures.
