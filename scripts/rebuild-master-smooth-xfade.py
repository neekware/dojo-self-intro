#!/usr/bin/env python3
"""Rebuild multilingual master with smooth crossfade between language clips."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "public/sections/13.00.00-multilingual/video/final"
OUT = FINAL / "multilingual-master-EN-FR-FA-JA-AR-ES-ZH.mp4"
OUT2 = ROOT / "public/sections/13.00.00-multilingual/video/04-multilingual-one-blur-switch.mp4"

ORDER = ["en", "fr", "fa", "ja", "ar", "es", "zh"]
XFADE = 0.9  # smooth dissolve duration


def probe(path: Path) -> float:
    return float(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            text=True,
        ).strip()
    )


def normalize(src: Path, dest: Path) -> None:
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-vf",
            "fps=24,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "17",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(dest),
        ]
    )


def main() -> None:
    clips = [FINAL / f"clip-{c}.mp4" for c in ORDER]
    for c in clips:
        assert c.exists(), c

    tmp = Path(tempfile.mkdtemp(prefix="ml-smooth-"))
    try:
        norms: list[Path] = []
        for i, c in enumerate(clips):
            n = tmp / f"n{i:02d}.mp4"
            normalize(c, n)
            norms.append(n)
            print("norm", c.name, f"{probe(n):.3f}s")

        durs = [probe(p) for p in norms]
        n = len(norms)

        # offset_i = start time of clip i in the output timeline
        offsets = [0.0]
        for i in range(1, n):
            offsets.append(offsets[-1] + durs[i - 1] - XFADE)

        inputs: list[str] = []
        for p in norms:
            inputs.extend(["-i", str(p)])

        # Smooth video dissolve (fade) + audio acrossfade chain
        v = "[0:v]null[v0];"
        a = "[0:a]anull[a0];"
        for i in range(1, n):
            prev = i - 1
            off = offsets[i]
            v += (
                f"[v{prev}][{i}:v]xfade=transition=fade:duration={XFADE}:offset={off:.4f}[v{i}];"
            )
            a += f"[a{prev}][{i}:a]acrossfade=d={XFADE}:c1=tri:c2=tri[a{i}];"

        fc = v + a
        last = n - 1
        cmd = [
            "ffmpeg",
            "-y",
            *inputs,
            "-filter_complex",
            fc,
            "-map",
            f"[v{last}]",
            "-map",
            f"[a{last}]",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(OUT),
        ]
        subprocess.check_call(cmd)
        shutil.copy2(OUT, OUT2)
        print("MASTER", OUT, f"{probe(OUT):.3f}s")
        print("also", OUT2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
