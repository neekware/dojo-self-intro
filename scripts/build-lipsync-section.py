#!/usr/bin/env python3
"""Build the LIP SYNC section: card -> real photo (VO) -> full talking clip.

The talking clip keeps its own audio in full — no VO over the performance.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "public/sections/09.10.00-lipsync"
OUT = SEC / "video/final/LOCKED-09.10-lipsync.mp4"

CARD = SEC / "after/final/title-card-lipsync.png"
STILL = SEC / "before/01-character-still.jpg"
TALK = SEC / "video/01-lipsync-talk.mp4"
VO = SEC / "audio/final/lipsync-eve-vo.mp3"

CARD_HOLD = 1.500
PAD_IN = 0.250
PAD_OUT = 0.700
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
    for p in (CARD, STILL, TALK, VO):
        if not p.exists():
            raise SystemExit(f"missing: {p}")

    vo_d = dur(VO)
    still_hold = PAD_IN + vo_d + PAD_OUT
    stills_end = CARD_HOLD + still_hold
    delay = int((CARD_HOLD + PAD_IN) * 1000)
    print(f"VO={vo_d:.3f} card={CARD_HOLD} still={still_hold:.3f} "
          f"end={stills_end:.3f} talk={dur(TALK):.3f}")

    with tempfile.TemporaryDirectory(prefix="dojo-lipsync-") as td:
        tmp = Path(td)

        stills = tmp / "stills.mp4"
        run([
            "ffmpeg", "-y",
            "-loop", "1", "-t", f"{CARD_HOLD:.3f}", "-i", str(CARD),
            "-loop", "1", "-t", f"{still_hold:.3f}", "-i", str(STILL),
            "-i", str(VO),
            "-filter_complex",
            f"[0:v]{NORM_V},setpts=PTS-STARTPTS[v0];"
            f"[1:v]{NORM_V},setpts=PTS-STARTPTS[v1];"
            f"[v0][v1]concat=n=2:v=1:a=0[v];"
            f"[2:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"adelay={delay}|{delay},apad,atrim=0:{stills_end:.3f},asetpts=PTS-STARTPTS[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{stills_end:.3f}", *ENC, str(stills),
        ])

        talk = tmp / "talk.mp4"
        run([
            "ffmpeg", "-y", "-i", str(TALK),
            "-filter_complex",
            f"[0:v]{NORM_V},setpts=PTS-STARTPTS[v];"
            "[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a]",
            "-map", "[v]", "-map", "[a]", *ENC, str(talk),
        ])

        OUT.parent.mkdir(parents=True, exist_ok=True)
        run([
            "ffmpeg", "-y", "-i", str(stills), "-i", str(talk),
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
