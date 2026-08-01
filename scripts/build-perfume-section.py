#!/usr/bin/env python3
"""Build the perfume section: title card -> prompt text -> generated image -> orbit video."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "public/sections/07.00.00-dojox-perfume"
OUT = SEC / "video/final/LOCKED-07-perfume.mp4"

CARD = SEC / "after/final/title-card-product-shot-perfume.png"
PROMPT = SEC / "after/final/prompt-card.png"
HERO = SEC / "after/01-perfume-dojox-hero.png"
ORBIT = SEC / "video/01-perfume-orbit.mp4"
VO = SEC / "audio/final/perfume-eve-vo.mp3"

CARD_HOLD = 1.500
PAD_IN = 0.250
PAD_OUT = 0.400
FADE = 0.300
PROMPT_SHARE = 0.45  # of the VO stills block

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
    for p in (CARD, PROMPT, HERO, ORBIT, VO):
        if not p.exists():
            raise SystemExit(f"missing: {p}")

    vo_d = dur(VO)
    stills_block = PAD_IN + vo_d + PAD_OUT
    prompt_hold = stills_block * PROMPT_SHARE
    hero_hold = stills_block - prompt_hold
    stills_end = CARD_HOLD + stills_block
    print(f"VO={vo_d:.3f} card={CARD_HOLD} prompt={prompt_hold:.3f} "
          f"hero={hero_hold:.3f} stills_end={stills_end:.3f}")

    delay = int((CARD_HOLD + PAD_IN) * 1000)

    with tempfile.TemporaryDirectory(prefix="dojo-perfume-") as td:
        tmp = Path(td)
        stills = tmp / "stills.mp4"
        run([
            "ffmpeg", "-y",
            "-loop", "1", "-t", f"{CARD_HOLD:.3f}", "-i", str(CARD),
            "-loop", "1", "-t", f"{prompt_hold:.3f}", "-i", str(PROMPT),
            "-loop", "1", "-t", f"{hero_hold:.3f}", "-i", str(HERO),
            "-i", str(VO),
            "-filter_complex",
            f"[0:v]{NORM_V},setpts=PTS-STARTPTS[v0];"
            f"[1:v]{NORM_V},setpts=PTS-STARTPTS[v1];"
            f"[2:v]{NORM_V},setpts=PTS-STARTPTS[v2];"
            f"[v0][v1][v2]concat=n=3:v=1:a=0[v];"
            f"[3:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"adelay={delay}|{delay},apad,atrim=0:{stills_end:.3f},asetpts=PTS-STARTPTS[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{stills_end:.3f}", *ENC, str(stills),
        ])

        orbit = tmp / "orbit.mp4"
        run([
            "ffmpeg", "-y", "-i", str(ORBIT),
            "-filter_complex",
            f"[0:v]{NORM_V},setpts=PTS-STARTPTS[v];"
            "[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a]",
            "-map", "[v]", "-map", "[a]", *ENC, str(orbit),
        ])

        run([
            "ffmpeg", "-y", "-i", str(stills), "-i", str(orbit),
            "-filter_complex",
            f"[0:v]format=yuv420p,fps=30,setsar=1,setpts=PTS-STARTPTS,"
            f"tpad=stop_mode=clone:stop_duration={FADE}[v0h];"
            f"[1:v]format=yuv420p,fps=30,setsar=1,setpts=PTS-STARTPTS[v1];"
            f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];"
            f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d={FADE}[a1];"
            f"[v0h][v1]xfade=transition=fade:duration={FADE}:offset={stills_end:.6f}[v];"
            f"[a0][a1]concat=n=2:v=0:a=1[a]",
            "-map", "[v]", "-map", "[a]", *ENC, str(OUT),
        ])

    print(f"OUT {OUT} {dur(OUT):.3f}s")


if __name__ == "__main__":
    main()
