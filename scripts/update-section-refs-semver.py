#!/usr/bin/env python3
"""Rewrite path refs after NN-slug → NN.00.00-slug rename."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# longest / most specific first
FOLDER_MAP = [
    ("17-credits", "17.00.00-credits"),
    ("16-lane-assist", "02.20.00-lane-assist"),
    ("15-diagrams", "13.10.00-diagrams-equations"),
    ("14-kids-tutor", "14.00.00-kids-tutor"),
    ("13-multilingual", "13.00.00-multilingual"),
    ("12-character-life", "12.00.00-character-life"),
    ("11-lipsync", "11.00.00-lipsync"),
    ("10-full-reel", "99.00.00-full-reel"),
    ("09-promo-motion", "09.00.00-promo-motion"),
    ("08-character-voice", "08.00.00-character-voice"),
    ("07-tryon", "07.00.00-tryon"),
    ("06-architecture-hq", "06.00.00-architecture-hq"),
    ("05-product-shot-perfume", "05.00.00-product-shot-perfume"),
    ("04-product-shot-coffee", "04.00.00-product-shot-coffee"),
    ("03-product-combine", "03.00.00-product-combine"),
    ("02-code", "02.00.00-stt-talk"),
    ("01-what-is-dojo", "01.00.00-what-is-dojo"),
    ("00-brand", "00.00.00-brand"),
]

SKIP_DIRS = {".git", "node_modules", "out", "dist", ".dojo"}
TEXT_EXT = {
    ".md",
    ".txt",
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".yml",
    ".yaml",
    ".mjs",
    ".cjs",
    ".css",
    ".html",
}


def main() -> None:
    changed = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_EXT and path.name != "DOJO.md":
            continue
        if set(path.parts) & SKIP_DIRS:
            continue
        if path.stat().st_size > 2_000_000:
            continue
        # don't rewrite this script's map keys into values twice if re-run on itself mid-write
        if path.name in {
            "rename-sections-semver.py",
            "update-section-refs-semver.py",
        }:
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        out = raw
        for old, new in FOLDER_MAP:
            out = out.replace(old, new)
        if out != raw:
            path.write_text(out, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))

    print(f"updated {len(changed)} files")
    for c in changed:
        print(" ", c)


if __name__ == "__main__":
    main()
