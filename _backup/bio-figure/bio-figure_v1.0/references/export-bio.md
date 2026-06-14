# Export — style, font, size, DPI, overlap self-check

## 1. Global style (English Arial, Nature-ish)

Put this at the top of every plotting script, before any `plt.subplots`:

```python
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "pdf.fonttype": 42,       # TrueType — editable in Illustrator
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    "font.size": 7,
    "axes.titlesize": 8,
    "axes.labelsize": 7,
    "xtick.labelsize": 6,
    "ytick.labelsize": 6,
    "legend.fontsize": 6,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.8,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "legend.frameon": False,
    "figure.dpi": 150,          # screen preview; export DPI is set separately
})
```

If Arial is missing, matplotlib falls back to Helvetica → DejaVu Sans. **Mention the fallback in the report** so the user knows the rendered font may differ from a true Arial submission.

## 2. Figure sizing

- Single column ≈ 85 mm (≈ 3.35 in).
- 1.5 column ≈ 114 mm (≈ 4.49 in).
- Double column ≈ 170 mm (≈ 6.69 in).
- Height: pick so axes ≈ 1:1 to ~3:4 unless the data demands otherwise; keep tick + label space.

```python
fig, ax = plt.subplots(figsize=(3.35, 2.6))  # single-column default
```

## 3. Export

Always export both PDF (vector, editable) and PNG (review / web):

```python
def save_bio_fig(fig, stem, png_dpi=600):
    fig.savefig(f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(f"{stem}.png", dpi=png_dpi, bbox_inches="tight")
```

- `stem` is a descriptive name (e.g. `volcano_TvsC`), **not** `figure1`.
- Do not rely on `bbox_inches="tight"` to recover from a too-small canvas: size correctly first.

## 4. Overlap self-check (mandatory)

Two checks every figure must pass before delivery.

### 4.1 Legend occlusion

**Do not** use the naive "legend bbox ∩ data bbox" test — it over-reports because data may not actually fill the bbox.

Preferred strategy: **place the legend outside the axes by default** and grow the figure width accordingly:

```python
leg = ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0),
                borderaxespad=0.0, frameon=False)
fig.subplots_adjust(right=0.78)  # leave room for the legend
```

If the user insists on an in-axes legend, do a real pixel-level check after drawing:

```python
def legend_overlaps_data(fig, ax, legend):
    fig.canvas.draw()
    # legend bbox in display coords
    bbox = legend.get_window_extent()
    img = np.asarray(fig.canvas.buffer_rgba())  # H × W × 4
    h, w = img.shape[:2]
    x0, x1 = max(0, int(bbox.x0)), min(w, int(bbox.x1))
    # display coords have origin at lower-left; convert to image-row coords
    y0, y1 = max(0, h - int(bbox.y1)), min(h, h - int(bbox.y0))
    region = img[y0:y1, x0:x1]
    # background pixels are near-white; anything else means a marker / line / text from the data
    non_bg = np.any(region[..., :3] < 245, axis=-1)
    # mask out the legend's own pixels by clipping to ax bbox
    ax_bbox = ax.get_window_extent()
    ax_x0, ax_x1 = max(0, int(ax_bbox.x0)), min(w, int(ax_bbox.x1))
    ax_y0, ax_y1 = max(0, h - int(ax_bbox.y1)), min(h, h - int(ax_bbox.y0))
    # ratio of data pixels inside the legend region
    return non_bg.mean() > 0.02
```

If positive → move the legend outside, or switch to direct in-figure labelling.

For a small number of fixed categories (e.g. 2–4 KM strata), prefer **direct in-figure annotation** over a legend.

### 4.2 Text-label overlap

Common offenders: volcano gene labels, UMAP cluster labels, forest variable names.

- If `adjustText` is installed:

  ```python
  from adjustText import adjust_text
  texts = [ax.text(x_i, y_i, label_i) for x_i, y_i, label_i in top_n_points]
  adjust_text(texts, ax=ax,
              arrowprops=dict(arrowstyle="-", lw=0.5, color="grey"))
  ```

- If not installed, fall back to a small jitter / repulsion routine on the top-N points, and warn the user the de-overlap quality is lower.

- **Hard limit:** only label top-N (default `N = 10` for volcano; `N = clusters` for UMAP). Never label every point.

### 4.3 Reporting

Record the outcome in `report.md`:

```
- Overlap check: passed
- Overlap check: adjusted (legend moved outside axes, 12 gene labels repositioned)
```

## 5. Common pitfalls

- Setting `font.size` after creating axes — the tick labels keep the old size. Set `rcParams` first.
- Saving PDF with `pdf.fonttype = 3` (Type 3) — text is not editable / searchable. Always 42.
- Using `transparent=True` and a colorbar — produces a half-transparent gradient that looks washed out on print.
- DPI < 600 on PNG — Nature requires ≥ 300 dpi but 600 is the safe default for review boards.
- Mixing inches and cm in `figsize`. matplotlib uses inches.
