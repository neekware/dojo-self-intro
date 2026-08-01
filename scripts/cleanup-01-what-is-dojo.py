#!/usr/bin/env python3
"""Lock-friendly cleanup for section 17 — drop generation leftovers, keep finals + rebuild sources."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

SEC = Path(__file__).resolve().parents[1] / "public/sections/01.00.00-what-is-dojo"

KEEP_EXACT = {
    SEC / "after/final/connection-hero-LOCKED.png",
    SEC / "audio/final/what-is-dojo-gem-vo.mp3",
    SEC / "video/final/LOCKED-01-connection.mp4",
    SEC / "video/final/LOCKED-01-what-is-dojo.mp4",
    SEC / "video/work/LOCKED-01-connection-forward-only-SOURCE.mp4",
    SEC / "video/work/necklace-neural-turn-taking-flow-SOURCE.mp4",
    SEC / "text/LOCKED.md",
    SEC / "text/NOTES.md",
}

# dirs that may stay empty
KEEP_DIRS = {
    SEC / "before",
    SEC / "after",
    SEC / "after/final",
    SEC / "after/work",
    SEC / "audio",
    SEC / "audio/final",
    SEC / "audio/work",
    SEC / "video",
    SEC / "video/final",
    SEC / "video/work",
    SEC / "text",
}


def main() -> None:
    if not SEC.is_dir():
        raise SystemExit(f"missing {SEC}")

    removed: list[str] = []
    for path in sorted(SEC.rglob("*"), reverse=True):
        if path.is_dir():
            # remove empty leftover dirs outside keep set (e.g. superseded, loop-smooth)
            if path in KEEP_DIRS or path == SEC:
                continue
            # if dir still has keep files under it, skip
            if any(p in path.parents or p == path for p in KEEP_EXACT):
                # only delete if no kept files inside
                if any(k.is_relative_to(path) for k in KEEP_EXACT if k.exists()):
                    continue
            try:
                if not any(path.iterdir()):
                    path.rmdir()
                    removed.append(f"dir {path.relative_to(SEC)}")
                elif path.name in {"superseded", "loop-smooth", "frames"} or "loop-smooth" in path.parts:
                    shutil.rmtree(path)
                    removed.append(f"tree {path.relative_to(SEC)}")
            except OSError:
                pass
            continue

        if path.name == ".DS_Store":
            path.unlink()
            removed.append(str(path.relative_to(SEC)))
            continue

        if path in KEEP_EXACT:
            continue

        # delete everything else under section
        path.unlink()
        removed.append(str(path.relative_to(SEC)))

    # second pass: empty dirs
    for path in sorted(SEC.rglob("*"), reverse=True):
        if path.is_dir() and path not in KEEP_DIRS and path != SEC:
            try:
                if not any(path.iterdir()):
                    path.rmdir()
                    removed.append(f"dir {path.relative_to(SEC)}")
            except OSError:
                pass

    print("removed", len(removed), "items")
    for r in removed[:80]:
        print(" -", r)
    if len(removed) > 80:
        print(f" ... +{len(removed) - 80} more")

    print("\nremaining:")
    for p in sorted(SEC.rglob("*")):
        if p.is_file():
            print(" ", p.relative_to(SEC), p.stat().st_size)

    for rel in [
        "video/final/LOCKED-01-connection.mp4",
        "video/final/LOCKED-01-what-is-dojo.mp4",
        "audio/final/what-is-dojo-gem-vo.mp3",
    ]:
        f = SEC / rel
        d = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(f),
            ],
            text=True,
        ).strip()
        print(f"DUR {rel} = {d}s")


if __name__ == "__main__":
    main()
