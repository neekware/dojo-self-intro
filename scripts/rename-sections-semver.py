#!/usr/bin/env python3
"""Rename public/sections/NN-slug → NN.00.00-slug (major.minor.patch).

Majors land on .00.00 so inserts can use minor/patch without cascading:
  01.00.00-what-is-dojo
  01.10.00-new-beat      ← minor insert after intro
  01.00.10-tiny-fix     ← patch insert
  02.00.00-stt-talk
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections"

# old integer folder → (major, minor, patch) — film order majors
# Keep stable majors matching previous integer ids after the 01-insert cascade.
OLD_TO_VER: dict[str, tuple[int, int, int]] = {
    "00-brand": (0, 0, 0),
    "01-what-is-dojo": (1, 0, 0),
    "02-code": (2, 0, 0),
    "03-product-combine": (3, 0, 0),
    "04-product-shot-coffee": (4, 0, 0),
    "05-product-shot-perfume": (5, 0, 0),
    "06-architecture-hq": (6, 0, 0),
    "07-tryon": (7, 0, 0),
    "08-character-voice": (8, 0, 0),
    "09-promo-motion": (9, 0, 0),
    "10-full-reel": (10, 0, 0),
    "11-lipsync": (11, 0, 0),
    "12-character-life": (12, 0, 0),
    "13-multilingual": (13, 0, 0),
    "14-kids-tutor": (14, 0, 0),
    "15-diagrams": (15, 0, 0),
    "16-lane-assist": (16, 0, 0),
    "17-credits": (17, 0, 0),
}


def ver_name(major: int, minor: int, patch: int, slug: str) -> str:
    return f"{major:02d}.{minor:02d}.{patch:02d}-{slug}"


def main() -> None:
    renames: list[tuple[Path, Path]] = []
    for old_name, (maj, minor, patch) in OLD_TO_VER.items():
        src = SEC / old_name
        if not src.is_dir():
            # already semver?
            if list(SEC.glob(f"*.*.*-{old_name.split('-', 1)[-1]}")):
                print("skip missing (maybe done):", old_name)
                continue
            raise SystemExit(f"missing {src}")
        slug = old_name.split("-", 1)[1]
        dest = SEC / ver_name(maj, minor, patch, slug)
        if dest.exists():
            raise SystemExit(f"dest exists {dest}")
        renames.append((src, dest))

    # rename high majors first not needed — names don't collide (dots vs no dots)
    for src, dest in renames:
        print(f"{src.name} → {dest.name}")
        src.rename(dest)

    print("done", len(renames), "folders")


if __name__ == "__main__":
    main()
