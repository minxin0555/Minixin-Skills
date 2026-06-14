#!/usr/bin/env python3
"""palette.py — color tools for bio-figure.

Pure standard library for all color math (sRGB <-> linear RGB <-> XYZ <-> Lab <-> LCh,
plus Brettel-style colorblind simulation). Only the `swatch` subcommand reaches for
matplotlib to render a PNG.

Subcommands:
    sequential   --hue <hex|deg> -n 7
    diverging    --low <hex> --high <hex> -n 9
    two-color    [--seed <hex>]
    qualitative  -n 8 [--journal npg|aaas|nejm|lancet|jco|okabe-ito|tableau10]
    check        <hex...>
    swatch       <hex...> -o card.png

Each subcommand prints hex codes (one per line) to stdout, except `check` (which
prints a small table) and `swatch` (which writes a PNG).
"""
from __future__ import annotations

import argparse
import math
import sys
from typing import Iterable, List, Tuple

# ----------------------------- color space -----------------------------------

# D65 reference white in XYZ.
WHITE_D65 = (0.95047, 1.00000, 1.08883)

# sRGB <-> linear RGB (IEC 61966-2-1).
def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def linear_to_srgb(c: float) -> float:
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055

# Linear RGB <-> XYZ (D65, sRGB primaries).
_M_RGB2XYZ = (
    (0.4124564, 0.3575761, 0.1804375),
    (0.2126729, 0.7151522, 0.0721750),
    (0.0193339, 0.1191920, 0.9503041),
)
_M_XYZ2RGB = (
    ( 3.2404542, -1.5371385, -0.4985314),
    (-0.9692660,  1.8760108,  0.0415560),
    ( 0.0556434, -0.2040259,  1.0572252),
)

def _matmul3(M, v):
    return tuple(M[i][0]*v[0] + M[i][1]*v[1] + M[i][2]*v[2] for i in range(3))

def rgb_to_xyz(r: float, g: float, b: float) -> Tuple[float, float, float]:
    lin = (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b))
    return _matmul3(_M_RGB2XYZ, lin)

def xyz_to_rgb(x: float, y: float, z: float) -> Tuple[float, float, float]:
    lin = _matmul3(_M_XYZ2RGB, (x, y, z))
    return tuple(linear_to_srgb(c) for c in lin)

# XYZ <-> Lab (CIELAB, D65).
def _f(t: float) -> float:
    return t ** (1/3) if t > 216/24389 else (841/108) * t + 4/29

def _finv(t: float) -> float:
    return t ** 3 if t > 6/29 else (t - 4/29) * (108/841)

def xyz_to_lab(x: float, y: float, z: float) -> Tuple[float, float, float]:
    fx = _f(x / WHITE_D65[0])
    fy = _f(y / WHITE_D65[1])
    fz = _f(z / WHITE_D65[2])
    return (116*fy - 16, 500*(fx - fy), 200*(fy - fz))

def lab_to_xyz(L: float, a: float, b: float) -> Tuple[float, float, float]:
    fy = (L + 16) / 116
    fx = fy + a / 500
    fz = fy - b / 200
    return (
        WHITE_D65[0] * _finv(fx),
        WHITE_D65[1] * _finv(fy),
        WHITE_D65[2] * _finv(fz),
    )

# Lab <-> LCh (polar CIELAB; treated here as HCL for the CLI).
def lab_to_lch(L: float, a: float, b: float) -> Tuple[float, float, float]:
    C = math.hypot(a, b)
    h = math.degrees(math.atan2(b, a)) % 360.0
    return (L, C, h)

def lch_to_lab(L: float, C: float, h: float) -> Tuple[float, float, float]:
    rad = math.radians(h)
    return (L, C * math.cos(rad), C * math.sin(rad))

# Convenience: hex <-> tuple (0..1) and Lab/LCh wrappers.
def hex_to_rgb(s: str) -> Tuple[float, float, float]:
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(ch*2 for ch in s)
    if len(s) != 6:
        raise ValueError(f"invalid hex: {s!r}")
    return tuple(int(s[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def rgb_to_hex(r: float, g: float, b: float) -> str:
    return "#{:02X}{:02X}{:02X}".format(
        max(0, min(255, round(r * 255))),
        max(0, min(255, round(g * 255))),
        max(0, min(255, round(b * 255))),
    )

def hex_to_lch(s: str) -> Tuple[float, float, float]:
    r, g, b = hex_to_rgb(s)
    return lab_to_lch(*xyz_to_lab(*rgb_to_xyz(r, g, b)))

def lch_to_hex(L: float, C: float, h: float) -> str:
    return rgb_to_hex(*xyz_to_rgb(*lab_to_xyz(*lch_to_lab(L, C, h))))

# ----------------------------- colorblind sim --------------------------------
# Approximate sRGB-domain Brettel-style matrices for severe protanopia,
# deuteranopia, and tritanopia. These are widely cited approximations used for
# screening colorblind safety; they are not a medical-grade simulation but are
# adequate for "did two categories collapse into the same color".

_CB_MATRICES = {
    "protan": (
        (0.567, 0.433, 0.000),
        (0.558, 0.442, 0.000),
        (0.000, 0.242, 0.758),
    ),
    "deutan": (
        (0.625, 0.375, 0.000),
        (0.700, 0.300, 0.000),
        (0.000, 0.300, 0.700),
    ),
    "tritan": (
        (0.950, 0.050, 0.000),
        (0.000, 0.433, 0.567),
        (0.000, 0.475, 0.525),
    ),
}

def simulate_cb(hex_color: str, kind: str) -> str:
    r, g, b = hex_to_rgb(hex_color)
    M = _CB_MATRICES[kind]
    rr = M[0][0]*r + M[0][1]*g + M[0][2]*b
    gg = M[1][0]*r + M[1][1]*g + M[1][2]*b
    bb = M[2][0]*r + M[2][1]*g + M[2][2]*b
    return rgb_to_hex(rr, gg, bb)

# WCAG relative luminance and contrast ratio.
def relative_luminance(hex_color: str) -> float:
    r, g, b = hex_to_rgb(hex_color)
    rl = srgb_to_linear(r); gl = srgb_to_linear(g); bl = srgb_to_linear(b)
    return 0.2126*rl + 0.7152*gl + 0.0722*bl

def wcag_contrast(c1: str, c2: str) -> float:
    L1, L2 = relative_luminance(c1), relative_luminance(c2)
    a, b = max(L1, L2), min(L1, L2)
    return (a + 0.05) / (b + 0.05)

# ----------------------------- palettes --------------------------------------
JOURNAL_PALETTES = {
    "okabe-ito": [
        "#000000", "#E69F00", "#56B4E9", "#009E73",
        "#F0E442", "#0072B2", "#D55E00", "#CC79A7",
    ],
    "npg": [
        "#E64B35", "#4DBBD5", "#00A087", "#3C5488",
        "#F39B7F", "#8491B4", "#91D1C2", "#DC0000",
        "#7E6148", "#B09C85",
    ],
    "aaas": [
        "#3B4992", "#EE0000", "#008B45", "#631879",
        "#008280", "#BB0021", "#5F559B", "#A20056",
        "#808180", "#1B1919",
    ],
    "nejm": [
        "#BC3C29", "#0072B5", "#E18727", "#20854E",
        "#7876B1", "#6F99AD", "#FFDC91", "#EE4C97",
    ],
    "lancet": [
        "#00468B", "#ED0000", "#42B540", "#0099B4",
        "#925E9F", "#FDAF91", "#AD002A", "#ADB6B6",
        "#1B1919",
    ],
    "jco": [
        "#0073C2", "#EFC000", "#868686", "#CD534C",
        "#7AA6DC", "#003C67", "#8F7700", "#3B3B3B",
    ],
    "tableau10": [
        "#4E79A7", "#F28E2B", "#E15759", "#76B7B2",
        "#59A14F", "#EDC948", "#B07AA1", "#FF9DA7",
        "#9C755F", "#BAB0AC",
    ],
}

DEFAULT_TWO_COLOR = ("#0072B2", "#E69F00")  # Okabe-Ito blue / orange

def parse_hue(arg: str) -> float:
    """Accept either '#xxxxxx' (extract hue) or a number in degrees.

    A bare numeric string ("240", "30.5") is always treated as degrees — never as
    a 3-char hex (which would silently turn "240" into #240240).
    """
    arg = arg.strip()
    if arg.startswith("#"):
        _, _, h = hex_to_lch(arg)
        return h
    try:
        return float(arg) % 360.0
    except ValueError:
        pass
    # No leading '#' but not purely numeric — try as hex (6 chars).
    _, _, h = hex_to_lch(arg)
    return h

def sequential(hue: float, n: int) -> List[str]:
    """Same-hue sequential: fix hue, chroma rises then plateaus, luminance drops."""
    n = max(2, n)
    out = []
    for i in range(n):
        t = i / (n - 1)            # 0 = lightest, 1 = darkest
        L = 95 - 70 * t            # 95 -> 25
        C = 20 + 50 * t            # 20 -> 70
        out.append(lch_to_hex(L, C, hue))
    return out

def diverging(low_hex: str, high_hex: str, n: int) -> List[str]:
    """Diverging through faint grey: low hue at left, faint grey center, high hue at right."""
    n = max(3, n)
    _, C_lo, h_lo = hex_to_lch(low_hex)
    _, C_hi, h_hi = hex_to_lch(high_hex)
    out = []
    for i in range(n):
        t = i / (n - 1)            # 0..1
        # luminance: V-shape peaking at the center
        L = 35 + 55 * (1 - abs(2*t - 1))  # 35 at ends, 90 at center
        if t < 0.5:
            s = 1 - 2*t            # 1 at far left, 0 at center
            C = C_lo * s
            hue = h_lo
        else:
            s = 2*t - 1            # 0 at center, 1 at far right
            C = C_hi * s
            hue = h_hi
        out.append(lch_to_hex(L, C, hue))
    return out

def two_color(seed_hex: str | None) -> Tuple[str, str]:
    if seed_hex is None:
        return DEFAULT_TWO_COLOR
    L, C, h = hex_to_lch(seed_hex)
    # complement = same L/C, hue + 180.
    return seed_hex, lch_to_hex(L, max(C, 40), (h + 180) % 360)

def qualitative(journal: str, n: int) -> List[str]:
    key = journal.lower()
    if key not in JOURNAL_PALETTES:
        raise ValueError(f"unknown journal palette: {journal!r}; choose from {sorted(JOURNAL_PALETTES)}")
    palette = JOURNAL_PALETTES[key]
    if n > len(palette):
        raise ValueError(f"{journal} has only {len(palette)} colors; asked for {n}")
    return palette[:n]

# ----------------------------- CLI -------------------------------------------
def _print_hex_list(colors: Iterable[str]) -> None:
    for c in colors:
        print(c)

def cmd_sequential(args):
    hue = parse_hue(args.hue)
    _print_hex_list(sequential(hue, args.n))

def cmd_diverging(args):
    _print_hex_list(diverging(args.low, args.high, args.n))

def cmd_two_color(args):
    a, b = two_color(args.seed)
    _print_hex_list([a, b])

def cmd_qualitative(args):
    _print_hex_list(qualitative(args.journal, args.n))

def cmd_check(args):
    hdr = ("hex", "protan", "deutan", "tritan", "vs#FFF", "vs#000")
    print("\t".join(hdr))
    for c in args.colors:
        row = (
            c,
            simulate_cb(c, "protan"),
            simulate_cb(c, "deutan"),
            simulate_cb(c, "tritan"),
            f"{wcag_contrast(c, '#FFFFFF'):.2f}",
            f"{wcag_contrast(c, '#000000'):.2f}",
        )
        print("\t".join(row))

def cmd_swatch(args):
    try:
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
    except ImportError:
        sys.exit("matplotlib is required for `swatch`; install with `pip install matplotlib`")
    colors = list(args.colors)
    n = len(colors)
    fig_w = max(2.0, 0.9 * n)
    fig, ax = plt.subplots(figsize=(fig_w, 1.6))
    ax.set_xlim(0, n); ax.set_ylim(0, 1)
    ax.axis("off")
    for i, c in enumerate(colors):
        ax.add_patch(Rectangle((i, 0.25), 1, 0.55, facecolor=c, edgecolor="none"))
        text_color = "#FFFFFF" if relative_luminance(c) < 0.45 else "#000000"
        ax.text(i + 0.5, 0.525, c, ha="center", va="center",
                fontsize=7, color=text_color, family="sans-serif")
    fig.tight_layout()
    fig.savefig(args.output, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {args.output}")

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="color tools for bio-figure")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sequential", help="same-hue sequential ramp")
    s.add_argument("--hue", required=True, help="hex (#RRGGBB) or hue in degrees")
    s.add_argument("-n", type=int, default=7)
    s.set_defaults(func=cmd_sequential)

    s = sub.add_parser("diverging", help="diverging ramp through faint grey")
    s.add_argument("--low", required=True, help="low-end hex")
    s.add_argument("--high", required=True, help="high-end hex")
    s.add_argument("-n", type=int, default=9)
    s.set_defaults(func=cmd_diverging)

    s = sub.add_parser("two-color", help="two-class palette")
    s.add_argument("--seed", default=None, help="seed hex (omit for blue/orange Okabe-Ito)")
    s.set_defaults(func=cmd_two_color)

    s = sub.add_parser("qualitative", help="qualitative journal palette")
    s.add_argument("--journal", default="okabe-ito",
                   choices=sorted(JOURNAL_PALETTES.keys()))
    s.add_argument("-n", type=int, default=8)
    s.set_defaults(func=cmd_qualitative)

    s = sub.add_parser("check", help="colorblind sim + WCAG contrast")
    s.add_argument("colors", nargs="+")
    s.set_defaults(func=cmd_check)

    s = sub.add_parser("swatch", help="render a swatch PNG (matplotlib)")
    s.add_argument("colors", nargs="+")
    s.add_argument("-o", "--output", required=True)
    s.set_defaults(func=cmd_swatch)

    return p

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    main()
