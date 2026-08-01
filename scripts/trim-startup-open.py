#!/usr/bin/env python3
"""Trim startup open: keep 2.050s → 16.561s (frame-accurate re-encode)."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "public/sections/00.00.00-brand/video/final/00-dojo-startup-open.mp4"
# also keep untrimmed backup
BAK = ROOT / "public/sections/00.00.00-brand/video/final/00-dojo-startup-open-full.mp4"
OUT = ROOT / "public/sections/00.00.00-brand/video/final/00-dojo-startup-open.mp4"
TMP = ROOT / "public/sections/00.00.00-brand/video/final/_trim-startup.mp4"

START = 2.050
END = 16.561


def main() -> None:
    if not BAK.exists():
        subprocess.check_call(["cp", "-f", str(SRC), str(BAK)])

    # Frame-accurate: -ss after -i, re-encode (no libx264 on some envs — try libx264 then mpeg4)
    def run(vcodec: list[str]) -> None:
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(BAK),
                "-ss",
                str(START),
                "-to",
                str(END),
                "-map",
                "0:v:0",
                "-map",
                "0:a:0?",
                *vcodec,
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-movflags",
                "+faststart",
                str(TMP),
            ]
        )

    try:
        run(["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p"])
    except subprocess.CalledProcessError:
        # macOS fallback via videotoolbox if present
        try:
            run(["-c:v", "h264_videotoolbox", "-b:v", "8M", "-pix_fmt", "yuv420p"])
        except subprocess.CalledProcessError:
            run(["-c:v", "mpeg4", "-q:v", "3"])

    subprocess.check_call(["mv", "-f", str(TMP), str(OUT)])

    probe = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-show_entries",
            "stream=codec_name,width,height",
            "-of",
            "default=noprint_wrappers=1",
            str(OUT),
        ],
        text=True,
    )
    print(probe)
    print("kept", START, "→", END, "target_dur", END - START)
    print(OUT)


if __name__ == "__main__":
    main()
