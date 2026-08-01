#!/usr/bin/env python3
"""Build the Products chapter: source -> branded -> combined -> coffee -> perfume.

One continuous Eve VO across a still sequence. Renders to the product-combine
section as the chapter master.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "public/sections"
COMBINE = S / "05.00.00-dojox-combine"
OUT = COMBINE / "video/final/LOCKED-05-product-combine.mp4"
VO = COMBINE / "audio/final/product-combine-eve-vo.mp3"

PAD_IN = 0.250
PAD_OUT = 0.500

# Three individual Dojo X products, then the combined hero
BEATS = [
    (COMBINE / "after/01-bar-dojox.png", 1.0),
    (COMBINE / "after/02-chips-dojox.png", 1.0),
    (COMBINE / "after/03-can-dojox.png", 1.0),
    (COMBINE / "after/04-trio-combined.png", 2.2),
]

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


def main() -> None:
    for path, _ in BEATS:
        if not path.exists():
            raise SystemExit(f"missing beat: {path}")

    vo_d = dur(VO)
    total = PAD_IN + vo_d + PAD_OUT
    weight_sum = sum(w for _, w in BEATS)
    holds = [total * w / weight_sum for _, w in BEATS]
    print(f"VO={vo_d:.3f} total={total:.3f}")
    for (p, _), h in zip(BEATS, holds):
        print(f"  {h:5.3f}s  {p.name}")

    inputs: list[str] = []
    for (path, _), hold in zip(BEATS, holds):
        inputs += ["-loop", "1", "-t", f"{hold:.3f}", "-i", str(path)]
    inputs += ["-i", str(VO)]

    parts = "".join(f"[{i}:v]{NORM_V},setpts=PTS-STARTPTS[v{i}];" for i in range(len(BEATS)))
    chain = "".join(f"[v{i}]" for i in range(len(BEATS)))
    delay = int(PAD_IN * 1000)
    vo_idx = len(BEATS)

    with tempfile.TemporaryDirectory(prefix="dojo-products-"):
        run([
            "ffmpeg", "-y", *inputs,
            "-filter_complex",
            f"{parts}{chain}concat=n={len(BEATS)}:v=1:a=0[v];"
            f"[{vo_idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"adelay={delay}|{delay},apad,atrim=0:{total:.3f},asetpts=PTS-STARTPTS[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", *ENC, str(OUT),
        ])

    print(f"OUT {OUT} {dur(OUT):.3f}s")


if __name__ == "__main__":
    main()
