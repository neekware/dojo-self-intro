#!/usr/bin/env python3
"""Convert Dojo startup capture to preferred MP4 (H.264 + AAC + faststart)."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/00.00.00-brand"
SRC = Path("/Users/val/Movies/2026-07-31 13-31-21.mov")
OUT_DIR = SEC / "video/final"
BEFORE = SEC / "before"
OUT = OUT_DIR / "00-dojo-startup-open.mp4"
SRC_COPY = BEFORE / "00-dojo-startup-source.mov"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    BEFORE.mkdir(parents=True, exist_ok=True)

    # Already H.264 — stream-copy video, AAC audio, faststart
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(SRC),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0?",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(OUT),
        ]
    )

    # If copy path fails weirdly on some MOV, fall back to avconvert/libx264 isn't available
    # Verify output exists and has duration
    probe = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size",
            "-show_entries",
            "stream=codec_name,width,height",
            "-of",
            "default=noprint_wrappers=1",
            str(OUT),
        ],
        text=True,
    )
    print(probe)

    # Keep source nearby
    subprocess.check_call(["cp", "-f", str(SRC), str(SRC_COPY)])
    print("OUT", OUT, "bytes", OUT.stat().st_size)


if __name__ == "__main__":
    main()
