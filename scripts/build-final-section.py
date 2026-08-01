#!/usr/bin/env python3
"""Build the closing section: brand hero still + outro VO.

Lands the reel on the same gem/connection hero the brand opened with, so the
film closes the loop it started.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "public/sections"
SEC = S / "15.00.00-final"
OUT = SEC / "video/final/LOCKED-15-final.mp4"

HERO = S / "00.00.00-brand/after/final/brand-open-still-LOCKED-1920x1080.jpg"
VO = SEC / "audio/final/final-outro-vo.mp3"

PAD_IN = 0.400
PAD_OUT = 1.400      # let it breathe before black
FADE_OUT = 1.000     # fade to black at the very end

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
    for p in (HERO, VO):
        if not p.exists():
            raise SystemExit(f"missing: {p}")

    vo_d = dur(VO)
    total = PAD_IN + vo_d + PAD_OUT
    delay = int(PAD_IN * 1000)
    fade_st = max(0.0, total - FADE_OUT)
    print(f"VO={vo_d:.3f} total={total:.3f} fade_out@{fade_st:.3f}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    run([
        "ffmpeg", "-y",
        "-loop", "1", "-t", f"{total:.3f}", "-i", str(HERO),
        "-i", str(VO),
        "-filter_complex",
        f"[0:v]{NORM_V},setpts=PTS-STARTPTS,"
        f"fade=t=out:st={fade_st:.3f}:d={FADE_OUT}[v];"
        f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,"
        f"adelay={delay}|{delay},apad,atrim=0:{total:.3f},asetpts=PTS-STARTPTS,"
        f"afade=t=out:st={fade_st:.3f}:d={FADE_OUT}[a]",
        "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", *ENC, str(OUT),
    ])

    print(f"OUT {OUT} {dur(OUT):.3f}s")


if __name__ == "__main__":
    main()
