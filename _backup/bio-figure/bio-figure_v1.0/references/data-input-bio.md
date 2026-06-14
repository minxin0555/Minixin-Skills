# Data input, formats, column mapping, environment

## 1. Supported formats (Python-native)

| Format | Library | Notes |
|---|---|---|
| `.csv` / `.tsv` / `.txt` | `pandas.read_csv` | Auto-sniff delimiter for `.txt`. |
| `.xlsx` | `pandas.read_excel` (needs `openpyxl`) | First sheet by default; ask if multi-sheet. |
| `.h5ad` | `anndata.read_h5ad` (`scanpy`) | Single-cell. Use `adata.obs`, `adata.var`, `adata.obsm['X_umap']`. |
| `.mtx` + 10x dir | `scanpy.read_10x_mtx` | Expect `matrix.mtx[.gz]`, `barcodes.tsv[.gz]`, `features.tsv[.gz]`. |
| `.parquet` | `pandas.read_parquet` (`pyarrow`) | Large tabular data. |

## 2. Explicitly unsupported

- `.rds` and `.RData` are R-specific binary formats. **Do not silently fail.** Tell the user one of:
  1. Re-export from R: `saveRDS` result → `write.csv` / `write_tsv`.
  2. Use the R branch of this skill (requires R + ggplot2 locally).

## 3. Column-mapping confirmation (mandatory before plotting if ambiguous)

After `pandas` reads the file:

1. List the columns and the first 3 rows in a compact preview.
2. Infer the role of each key column using regex + heuristics, **e.g.** for a DEG table:
   - log2 fold-change: `^(log2)?[ _-]?(fold[ _-]?change|fc)$` (case-insensitive)
   - adjusted p-value: `padj|fdr|q[ _-]?value|adj[._ ]?p`
   - raw p-value: `^p[ _-]?value$|^p$`
   - gene symbol: `gene|symbol|hgnc|feature`
3. **Echo the mapping back in one line** for the user to accept/correct, *only* if any key column is ambiguous (multiple plausible matches, or no match). If the inference is unambiguous, proceed.
4. If the user corrects a mapping, persist it for the rest of this run.

Examples of when to *not* ask:
- Columns are literally `gene`, `log2FoldChange`, `padj` → proceed.

Examples of when to ask:
- Columns include both `pvalue` and `padj` → ask which to use for the y-axis.
- Two columns matching `gene` (`gene_id`, `gene_name`) → ask which to label.

## 4. Long vs wide layout

| Chart | Expected layout |
|---|---|
| Volcano, MA, Manhattan, GSEA | Long, one row per feature. |
| Heatmap, correlation, PCA input | Wide matrix (`gene × sample` or `sample × feature`). |
| Box / violin / bar / line / facet | Long (`group`, `value`, optionally `replicate`). |
| KM, ROC, forest | Long; KM and ROC need per-sample rows. |

If the user passes a wide table where long is needed, call `pandas.melt` and confirm.

## 5. Environment policy

- Run in a Python env that already has the required packages.
- **Never `pip install … --user` or install into `base` silently.** If a package is missing:
  1. List exactly what is missing.
  2. Show the install command for the active env (`pip install …` or `conda install -c conda-forge …`).
  3. Stop until the user gives the go-ahead.
- If another env-management skill is present at runtime, defer env choice to it; the bio-figure side still works the same way.

### Package map

| Need | Package |
|---|---|
| Base plotting | `matplotlib`, `seaborn` |
| Data | `pandas`, `numpy` |
| Stats | `scipy` |
| Excel read | `openpyxl` |
| Survival | `lifelines` |
| Classification metrics | `scikit-learn` |
| Single-cell read | `scanpy`, `anndata` |
| Label de-overlap (optional) | `adjustText` |
| Parquet | `pyarrow` |
| Network layout (optional) | `networkx` |
| GSEA (optional) | `gseapy` |

## 6. Robust read-with-preview snippet

```python
import pandas as pd
from pathlib import Path

def read_table(path):
    p = Path(path)
    if p.suffix in {".csv"}:
        df = pd.read_csv(p)
    elif p.suffix in {".tsv", ".txt"}:
        df = pd.read_csv(p, sep=None, engine="python")
    elif p.suffix in {".xlsx"}:
        df = pd.read_excel(p)
    elif p.suffix in {".parquet"}:
        df = pd.read_parquet(p)
    else:
        raise ValueError(f"Unsupported tabular format: {p.suffix}")
    return df

df = read_table(path)
print(f"shape={df.shape}, cols={list(df.columns)}")
print(df.head(3))
```

For `.h5ad`:

```python
import anndata as ad
adata = ad.read_h5ad(path)
print(adata)  # shows obs / var / obsm keys
```
