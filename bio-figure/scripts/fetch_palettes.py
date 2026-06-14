#!/usr/bin/env python3
"""fetch_palettes.py — optional inspiration scraper for palette ideas.

This is a *fallback* helper, not part of the default flow. The primary palette
strategy is algorithmic same-hue sequential / diverging (see `palette.py`) plus
the curated journal palettes baked into `palette.py`. Reach for this script only
when the user explicitly asks for "more inspiration" or wants to seed a
qualitative palette from an external source.

Sources it can pull from (no auth required, all return JSON):
- ColourLovers public palettes API     https://www.colourlovers.com/api/palettes
- Colormind /api/                       http://colormind.io/api/

It deliberately uses only `urllib` so there is no `requests` dependency.

Usage:
    fetch_palettes.py colourlovers --keywords scientific -n 5
    fetch_palettes.py colormind    --model default

Output is one palette per line, hex codes separated by spaces.

Network calls can fail; if they do, the script prints a single line to stderr
and exits non-zero. Treat the result as inspiration only — always pass the
chosen colors back through `palette.py check` for colorblind safety before use.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from typing import List


def _http_get_json(url: str, timeout: float = 10.0):
    req = urllib.request.Request(url, headers={"User-Agent": "bio-figure/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def fetch_colourlovers(keywords: str, n: int) -> List[List[str]]:
    qs = urllib.parse.urlencode({
        "keywords": keywords,
        "format": "json",
        "numResults": n,
        "sortBy": "rank",
    })
    url = f"https://www.colourlovers.com/api/palettes?{qs}"
    data = _http_get_json(url)
    out: List[List[str]] = []
    for p in data:
        colors = p.get("colors", [])
        out.append(["#" + c for c in colors])
    return out


def fetch_colormind(model: str = "default") -> List[List[str]]:
    url = "http://colormind.io/api/"
    body = json.dumps({"model": model}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10.0) as r:
        data = json.load(r)
    result = data.get("result", [])
    return [["#{:02X}{:02X}{:02X}".format(*rgb) for rgb in result]]


def main(argv=None):
    p = argparse.ArgumentParser(description="optional palette inspiration scraper")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("colourlovers", help="fetch top palettes from ColourLovers")
    s.add_argument("--keywords", default="scientific")
    s.add_argument("-n", type=int, default=5)

    s = sub.add_parser("colormind", help="fetch a palette from Colormind")
    s.add_argument("--model", default="default")

    args = p.parse_args(argv)
    try:
        if args.cmd == "colourlovers":
            palettes = fetch_colourlovers(args.keywords, args.n)
        elif args.cmd == "colormind":
            palettes = fetch_colormind(args.model)
        else:
            p.error(f"unknown subcommand: {args.cmd}")
            return
    except Exception as e:
        sys.stderr.write(f"fetch failed: {e}\n")
        sys.exit(1)

    for pal in palettes:
        print(" ".join(pal))


if __name__ == "__main__":
    main()
