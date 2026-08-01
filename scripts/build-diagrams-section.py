#!/usr/bin/env python3
"""Prepend the DIAGRAMS card to the locked diagrams sequence."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "public/sections/13.10.00-diagrams-equations"
OUT = SEC / "video/final/LOCKED-13.10-diagrams.mp4"

CARD = SEC / "after/final/title-card-diagrams.png"
MASTER = SEC / "video/final/LOCKED-diagrams-sequence.mp4"

CARD_HOLD = 1.500
FADE = 0.300

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
    for p in (CARD, MASTER):
        if not p.exists():
            raise SystemExit(f"missing: {p}")

    with tempfile.TemporaryDirectory(prefix="dojo-diag-") as td:
        tmp = Path(td)

        card = tmp / "card.mp4"
        run([
            "ffmpeg", "-y",
            "-loop", "1", "-t", f"{CARD_HOLD:.3f}", "-i", str(CARD),
            "-f", "lavfi", "-t", f"{CARD_HOLD:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
            "-filter_complex",
            f"[0:v]{NORM_V},setpts=PTS-STARTPTS[v];"
            f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{CARD_HOLD:.3f}", *ENC, str(card),
        ])

        body = tmp / "body.mp4"
        run([
            "ffmpeg", "-y", "-i", str(MASTER),
            "-filter_complex",
            f"[0:v]{NORM_V},setpts=PTS-STARTPTS[v];"
            "[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a]",
            "-map", "[v]", "-map", "[a]", *ENC, str(body),
        ])

        run([
            "ffmpeg", "-y", "-i", str(card), "-i", str(body),
            "-filter_complex",
            f"[0:v]format=yuv420p,fps=30,setsar=1,setpts=PTS-STARTPTS,"
            f"tpad=stop_mode=clone:stop_duration={FADE}[v0h];"
            f"[1:v]format=yuv420p,fps=30,setsar=1,setpts=PTS-STARTPTS[v1];"
            f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];"
            f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d={FADE}[a1];"
            f"[v0h][v1]xfade=transition=fade:duration={FADE}:offset={CARD_HOLD:.6f}[v];"
            f"[a0][a1]concat=n=2:v=0:a=1[a]",
            "-map", "[v]", "-map", "[a]", *ENC, str(OUT),
        ])

    print(f"OUT {OUT} {dur(OUT):.3f}s")


if __name__ == "__main__":
    main()
