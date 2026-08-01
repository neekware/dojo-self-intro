#!/usr/bin/env python3
"""Report per-section video vs audio duration drift."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "public/sections"

SECTIONS = [
    "01.00.00-what-is-dojo/video/final/CUMULATIVE-through-01.00.01.mp4",
    "02.00.00-stt-talk/video/final/LOCKED-02-stt.mp4",
    "02.10.00-tts-listen/video/final/LOCKED-03-woman-arc-opener.mp4",
    "02.10.00-tts-listen/video/final/LOCKED-03-tts-listen.mp4",
    "02.10.00-tts-listen/video/final/LOCKED-03-ears-listen.mp4",
    "02.20.00-lane-assist/video/final/LOCKED-lane-assist.mp4",
    "02.30.00-more-than-coding/video/final/LOCKED-02.30-more-than-coding.mp4",
    "03.00.00-tryon/video/final/LOCKED-03-tryon.mp4",
    "04.00.00-architecture-hq/video/final/LOCKED-04-architecture.mp4",
    "05.00.00-dojox-combine/video/final/LOCKED-05-product-combine.mp4",
    "06.00.00-dojox-coffee/video/final/LOCKED-06-coffee.mp4",
    "07.00.00-dojox-perfume/video/final/LOCKED-07-perfume.mp4",
    "09.00.00-promo-motion/video/final/LOCKED-09-promo.mp4",
    "09.10.00-lipsync/video/final/LOCKED-09.10-lipsync.mp4",
    "12.00.00-character-life/video/final/LOCKED-12-characters.mp4",
    "13.00.00-multilingual/video/final/LOCKED-13-multilingual.mp4",
    "13.10.00-diagrams-equations/video/final/LOCKED-13.10-diagrams-equations.mp4",
    "14.00.00-kids-tutor/video/final/LOCKED-14-kids-tutor.mp4",
    "15.00.00-final/video/final/LOCKED-15-final.mp4",
]


def probe(path: Path, stream: str) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", stream,
         "-show_entries", "stream=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)], text=True).strip()
    try:
        return float(out.splitlines()[0])
    except (ValueError, IndexError):
        return -1.0


def fmt(path: Path) -> float:
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)], text=True).strip())


def main() -> None:
    print(f"{'section':<34} {'video':>9} {'audio':>9} {'format':>9} {'drift':>8}")
    print("-" * 74)
    total_drift = 0.0
    for rel in SECTIONS:
        p = S / rel
        if not p.exists():
            print(f"{rel:<34} MISSING")
            continue
        v, a, f = probe(p, "v:0"), probe(p, "a:0"), fmt(p)
        drift = a - v
        total_drift += max(0.0, drift)
        flag = "  <-- FREEZE" if drift > 0.05 else ""
        name = rel.split("/")[0][:32]
        print(f"{name:<34} {v:9.3f} {a:9.3f} {f:9.3f} {drift:+8.3f}{flag}")
    print("-" * 74)
    print(f"cumulative video shortfall: {total_drift:.3f}s")


if __name__ == "__main__":
    main()
