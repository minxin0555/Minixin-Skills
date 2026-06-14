# Conclusion gate + statistic-integrity guardrail

## 1. What counts as a conclusion

A conclusion is a **falsifiable declarative sentence** about the data the figure is showing. It must be possible, in principle, to be wrong.

- ✓ "Gene `BRCA1` is significantly downregulated in tumour vs normal (log2FC = -2.1, padj = 1.4e-7)."
- ✓ "Patients in the high-`MYC` subgroup have shorter OS than the low-`MYC` subgroup (log-rank p = 0.003, median OS 14 vs 28 months)."
- ✓ "PC1 explains 38 % of variance and separates timepoints."
- ✗ "Show the difference between groups." (Topic, not a claim.)
- ✗ "Visualise expression patterns." (Topic.)
- ✗ "BRCA1 expression in tumour samples." (Description, no claim.)

## 2. When the user did not give a conclusion

1. Read the data and look at what the figure type can support.
2. Draft 1–2 candidate conclusions, both falsifiable, both grounded in what is actually computable from the data.
3. Show the candidates to the user; let them pick / amend with **one tap**. Do not block indefinitely.
4. If in **mode 0 (direct draw)**, do not block at all: auto-pick the most defensible candidate, proceed to plot, and put the conclusion into the figure caption / report.

## 3. Integrity guardrail (hard rule)

Any number that appears in a conclusion (p, FDR, q-value, HR, OR, log2FC, r, AUC, NES, median OS, …) must come from **one of two sources**:

- `[computed]` — this skill actually ran the statistic in this run.
- `[user-provided]` — taken from a result table the user supplied.

**You may not write a number from any other source.** No estimating from a figure, no "this looks significant" without a test, no transcribing a number the user mentioned in passing without checking it against a table.

### What to do when nothing is computed

If no statistic has been computed and no user table backs it up, write the conclusion in **question form**:

- "This figure examines whether `BRCA1` expression differs between tumour and normal."
- "This figure characterises the OS difference between high- and low-`MYC` subgroups."

Tag these `[question-form, no stats]` in the report.

## 4. Source tagging in the report

Every conclusion in `report.md` is tagged. Example:

```markdown
- Conclusion: BRCA1 is downregulated in tumour vs normal (log2FC = -2.1, padj = 1.4e-7). [computed]
- Conclusion: High-MYC subgroup has shorter OS (HR 1.7, 95% CI 1.2–2.4, p = 0.003). [user-provided — from `cox_results.csv`]
- Conclusion: This figure examines whether PC1 separates timepoints. [question-form, no stats]
```

## 5. Conclusion drives the rest of the workflow

- Chart choice: must visually argue this exact claim. If the conclusion says "A is higher than B in distribution", a bar of means is weaker than a box / violin.
- Palette: highlight the contrast in the conclusion (case vs control, up vs down).
- QA final check: read the conclusion, look at the figure — is the claim visible at a glance? If not, redesign.

## 6. Anti-patterns to refuse

- Inventing a `p = 0.03` for a chart that has no statistical test attached.
- Using a t-test p-value but writing the conclusion as if a Mann-Whitney was run (or vice versa).
- Computing a test on the wrong axis (e.g. comparing across the wrong groups) and reporting the unrelated number.
- Reporting `p < 0.05` for a multi-group comparison without correction.
- "Significant trend" without a regression / correlation actually being run.

When in doubt, fall back to question-form phrasing. Question-form is honest; an invented number is not.
