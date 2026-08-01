#!/usr/bin/env python3
"""Rebuild multilingual master with soft blur-dissolve between languages."""

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
XFADE = 1.15  # seconds of blur dissolve (first cut felt smoother)


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


def blur_dissolve(a: Path, b: Path, dest: Path, xfade: float = XFADE) -> None:
    """Soft blur + crossfade: picture goes fuzzy, next language blooms in."""
    da = probe(a)
    db = probe(b)
    if da <= xfade + 0.25 or db <= xfade + 0.25:
        raise SystemExit(f"clip too short for xfade={xfade}: {a}={da} {b}={db}")

    # Blur ramps on the outgoing tail and incoming head, then alpha crossfade.
    # sigma goes 0 → BLUR over the xfade window.
    blur = 18
    fc = (
        # split each input
        f"[0:v]split=2[a0][a1];"
        f"[1:v]split=2[b0][b1];"
        # main bodies (no transition)
        f"[a0]trim=0:{da - xfade:.4f},setpts=PTS-STARTPTS[amain];"
        f"[b1]trim={xfade:.4f}:{db:.4f},setpts=PTS-STARTPTS[bmain];"
        # transition tails/heads with progressive blur
        f"[a1]trim={da - xfade:.4f}:{da:.4f},setpts=PTS-STARTPTS,"
        f"gblur=sigma='{blur}*t/{xfade:.4f}':steps=3,format=yuva420p,"
        f"fade=t=out:st=0:d={xfade:.4f}:alpha=1[aend];"
        f"[b0]trim=0:{xfade:.4f},setpts=PTS-STARTPTS,"
        f"gblur=sigma='{blur}*(1-t/{xfade:.4f})':steps=3,format=yuva420p,"
        f"fade=t=in:st=0:d={xfade:.4f}:alpha=1[bstart];"
        # overlay dissolve (B over A with alpha)
        f"[aend][bstart]overlay=format=auto[x];"
        f"[amain][x][bmain]concat=n=3:v=1:a=0[v];"
        # audio crossfade
        f"[0:a][1:a]acrossfade=d={xfade:.4f}:c1=tri:c2=tri[a]"
    )

    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(a),
            "-i",
            str(b),
            "-filter_complex",
            fc,
            "-map",
            "[v]",
            "-map",
            "[a]",
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
            str(dest),
        ]
    )
    print("blur-dissolve", dest.name, f"{probe(dest):.2f}s")


def main() -> None:
    clips = [FINAL / f"clip-{c}.mp4" for c in ORDER]
    for c in clips:
        assert c.exists(), c

    tmp = Path(tempfile.mkdtemp(prefix="ml-blur-"))
    try:
        norms = []
        for i, c in enumerate(clips):
            n = tmp / f"n{i:02d}.mp4"
            normalize(c, n)
            norms.append(n)
            print("norm", c.name, probe(n))

        current = norms[0]
        for i in range(1, len(norms)):
            nxt = tmp / f"m{i:02d}.mp4"
            blur_dissolve(current, norms[i], nxt, XFADE)
            current = nxt

        shutil.copy2(current, OUT)
        shutil.copy2(current, OUT2)
        print("MASTER", OUT, f"{probe(OUT):.2f}s")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
