#!/usr/bin/env python3
"""Rewrite section path refs after inserting 01.00.00-what-is-dojo (cascade +1 for old 01-16)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Folder renames only (old_folder_prefix → new). Apply longest/highest first.
FOLDER_MAP = [
    ("01.00.00-what-is-dojo", "01.00.00-what-is-dojo"),  # old path string if any remain
    ("17.00.00-credits", "17.00.00-credits"),
    ("16.00.00-lane-assist", "02.20.00-lane-assist"),
    ("13.10.00-diagrams-equations", "13.10.00-diagrams-equations"),
    ("14.00.00-kids-tutor", "14.00.00-kids-tutor"),
    ("13.00.00-multilingual", "13.00.00-multilingual"),
    ("12.00.00-character-life", "12.00.00-character-life"),
    ("11.00.00-lipsync", "11.00.00-lipsync"),
    ("99.00.00-full-reel", "99.00.00-full-reel"),
    ("09.00.00-promo-motion", "09.00.00-promo-motion"),
    ("08.00.00-character-voice", "08.00.00-character-voice"),
    ("07.00.00-tryon", "07.00.00-tryon"),
    ("06.00.00-architecture-hq", "06.00.00-architecture-hq"),
    ("05.00.00-product-shot-perfume", "05.00.00-product-shot-perfume"),
    ("04.00.00-product-shot-coffee", "04.00.00-product-shot-coffee"),
    ("03.00.00-product-combine", "03.00.00-product-combine"),
    ("02.00.00-stt-talk", "02.00.00-stt-talk"),
]

# Deliverable filename renames for what-is-dojo
FILE_MAP = [
    ("LOCKED-01-what-is-dojo", "LOCKED-01-what-is-dojo"),
    ("LOCKED-01-connection", "LOCKED-01-connection"),
    ("LOCKED-01-cable-picture", "LOCKED-01-cable-picture"),  # historical refs
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
    ".toml",
    ".css",
    ".html",
    ".mjs",
    ".cjs",
}


def should_scan(path: Path) -> bool:
    if path.suffix.lower() not in TEXT_EXT and path.name not in {
        "DOJO.md",
        "README",
        "Dockerfile",
    }:
        # allow extensionless DOJO etc already covered
        if path.name not in {"DOJO.md"}:
            return False
    parts = set(path.parts)
    if parts & SKIP_DIRS:
        return False
    return True


def transform(text: str) -> str:
    out = text
    for old, new in FILE_MAP:
        out = out.replace(old, new)
    for old, new in FOLDER_MAP:
        out = out.replace(old, new)
    # section title headers like "# 17 — What is Dojo"
    out = re.sub(
        r"(?m)^(#{1,3}\s+)17(\s*[—-]\s*What is Dojo)",
        r"\g<1>01\2",
        out,
    )
    out = re.sub(
        r"(?m)^(#{1,3}\s+)16(\s*[—-]\s*Credits)",
        r"\g<1>17\2",
        out,
    )
    out = re.sub(
        r"(?m)^(#{1,3}\s+)15(\s*[—-]\s*Lane Assist)",
        r"\g<1>16\2",
        out,
    )
    out = re.sub(
        r"(?m)^(#{1,3}\s+)14(\s*[—-]\s*Diagrams)",
        r"\g<1>15\2",
        out,
    )
    out = re.sub(
        r"(?m)^(#{1,3}\s+)13(\s*[—-]\s*Kids)",
        r"\g<1>14\2",
        out,
    )
    out = re.sub(
        r"(?m)^(#{1,3}\s+)12(\s*[—-]\s*Multilingual)",
        r"\g<1>13\2",
        out,
    )
    # cleanup script name refs
    out = out.replace("cleanup-01.00.00-what-is-dojo", "cleanup-01.00.00-what-is-dojo")
    return out


def main() -> None:
    changed = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or not should_scan(path):
            continue
        # skip binary-ish large
        if path.stat().st_size > 2_000_000:
            continue
        try:
            raw = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        new = transform(raw)
        if new != raw:
            path.write_text(new, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))

    # rename cleanup script file if present
    old_script = ROOT / "scripts/cleanup-01.00.00-what-is-dojo.py"
    new_script = ROOT / "scripts/cleanup-01.00.00-what-is-dojo.py"
    if old_script.exists():
        old_script.rename(new_script)
        print("renamed", old_script.name, "→", new_script.name)

    print(f"updated {len(changed)} files")
    for c in changed:
        print(" ", c)


if __name__ == "__main__":
    main()
