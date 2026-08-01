#!/usr/bin/env python3
"""Place what-is-dojo between brand (00) and former 02.00.00-stt-talk.

Cascade: 01..16 → 02..17, then 01.00.00-what-is-dojo → 01.00.00-what-is-dojo.
Rename LOCKED-17* deliverables to LOCKED-01*.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections"


def main() -> None:
    src17 = SEC / "01.00.00-what-is-dojo"
    if not src17.is_dir():
        # already moved?
        if (SEC / "01.00.00-what-is-dojo").is_dir():
            print("already at 01.00.00-what-is-dojo")
        else:
            raise SystemExit("missing 01.00.00-what-is-dojo")
        return

    tmp = SEC / "_tmp-what-is-dojo"
    if tmp.exists():
        shutil.rmtree(tmp)
    src17.rename(tmp)
    print("parked", src17.name, "→", tmp.name)

    # map current folders by leading number
    by_num: dict[int, Path] = {}
    for p in SEC.iterdir():
        if not p.is_dir() or p.name.startswith("_"):
            continue
        m = re.match(r"^(\d+)-", p.name)
        if not m:
            continue
        by_num[int(m.group(1))] = p

    # shift 16→17 ... 01→02
    for n in range(16, 0, -1):
        if n not in by_num:
            raise SystemExit(f"missing section number {n:02d}")
        src = by_num[n]
        rest = src.name.split("-", 1)[1]
        dest = SEC / f"{n + 1:02d}-{rest}"
        if dest.exists():
            raise SystemExit(f"dest exists: {dest}")
        print(f"{src.name} → {dest.name}")
        src.rename(dest)
        by_num[n + 1] = dest
        del by_num[n]

    dest01 = SEC / "01.00.00-what-is-dojo"
    if dest01.exists():
        raise SystemExit(f"dest exists: {dest01}")
    tmp.rename(dest01)
    print(f"{tmp.name} → {dest01.name}")

    # rename LOCKED-17 → LOCKED-01 inside section
    renames = [
        (
            dest01 / "video/final/LOCKED-01-connection.mp4",
            dest01 / "video/final/LOCKED-01-connection.mp4",
        ),
        (
            dest01 / "video/final/LOCKED-01-what-is-dojo.mp4",
            dest01 / "video/final/LOCKED-01-what-is-dojo.mp4",
        ),
        (
            dest01 / "video/work/LOCKED-01-connection-forward-only-SOURCE.mp4",
            dest01 / "video/work/LOCKED-01-connection-forward-only-SOURCE.mp4",
        ),
    ]
    for a, b in renames:
        if a.exists():
            a.rename(b)
            print(f"file {a.name} → {b.name}")

    print("\nsections:")
    for p in sorted(SEC.iterdir()):
        if p.is_dir() and not p.name.startswith("."):
            print(" ", p.name)


if __name__ == "__main__":
    main()
