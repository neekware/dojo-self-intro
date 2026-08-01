#!/usr/bin/env python3
"""Merge the language cuts with a 300ms blur dissolve on each side of every join."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "public/sections/13.00.00-multilingual"
CUTS = SEC / "video/cuts"
OUT = CUTS / "merge-all-langs.mp4"

ORDER = ["en", "zh", "fa", "fr", "ar"]
BLUR = 0.300
SIGMA = 18

NORM_V = ("scale=1920:1080:flags=lanczos:force_original_aspect_ratio=decrease,"
          "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p")
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart"]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def dur(p: Path) -> float:
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)], text=True).strip())


def blur_join(a: Path, b: Path, out: Path) -> None:
    da, db = dur(a), dur(b)
    a_keep = max(0.0, da - BLUR)
    run([
        "ffmpeg", "-y", "-i", str(a), "-i", str(b),
        "-filter_complex",
        f"[0:v]{NORM_V},setpts=PTS-STARTPTS[v0];"
        f"[1:v]{NORM_V},setpts=PTS-STARTPTS[v1];"
        f"[v0]split[v0a][v0b];"
        f"[v0a]trim=0:{a_keep:.3f},setpts=PTS-STARTPTS[v0keep];"
        f"[v0b]trim={a_keep:.3f}:{da:.3f},setpts=PTS-STARTPTS,gblur=sigma={SIGMA}[v0blur];"
        f"[v1]split[v1a][v1b];"
        f"[v1a]trim=0:{BLUR:.3f},setpts=PTS-STARTPTS,gblur=sigma={SIGMA}[v1blur];"
        f"[v1b]trim={BLUR:.3f}:{db:.3f},setpts=PTS-STARTPTS[v1keep];"
        f"[v0blur][v1blur]xfade=transition=fade:duration={BLUR:.3f}:offset=0[vmid];"
        f"[v0keep][vmid][v1keep]concat=n=3:v=1:a=0[v];"
        f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];"
        f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a1];"
        f"[a0][a1]concat=n=2:v=0:a=1[a]",
        "-map", "[v]", "-map", "[a]", *ENC, str(out),
    ])


def main() -> None:
    clips = [CUTS / f"cut-{lang}.mp4" for lang in ORDER]
    for c in clips:
        if not c.exists():
            raise SystemExit(f"missing: {c}")

    with tempfile.TemporaryDirectory(prefix="dojo-lang-") as td:
        tmp = Path(td)
        cur = clips[0]
        for i, nxt in enumerate(clips[1:], 1):
            step = tmp / f"chain-{i}.mp4"
            print(f"join {i}: +{ORDER[i].upper()}")
            blur_join(cur, nxt, step)
            cur = step
        run(["ffmpeg", "-y", "-i", str(cur), "-c", "copy", str(OUT)])

    print(f"OUT {OUT} {dur(OUT):.3f}s")


if __name__ == "__main__":
    main()
