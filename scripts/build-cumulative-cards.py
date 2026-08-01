#!/usr/bin/env python3
"""Build cumulative preview with chapter title cards, then prune intermediates.

Order:
  intro cumulative (locked 0.25s seam)
  TALK card -> STT
  LISTEN card -> wall / eyes / ears
  CODING card -> Lane Assist
  MULTIMEDIA card -> More than coding

Cards hold 1.5s. Every join: outgoing preserved in full, incoming picture+audio
fade in over 300ms.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "public/sections"
OUT = S / "15.00.00-final/video/final/CUMULATIVE-through-15.00.00.mp4"

FADE = 0.300
CARD_HOLD = 1.500
PRESET = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p",
          "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart"]

NORM_V = ("scale=1920:1080:flags=lanczos:force_original_aspect_ratio=decrease,"
          "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def dur(p: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)], text=True).strip()
    return float(out)


def vdur(p: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)], text=True).strip()
    try:
        return float(out)
    except ValueError:
        return dur(p)


def card(png: Path, out: Path) -> None:
    run(["ffmpeg", "-y", "-loop", "1", "-i", str(png), "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-filter_complex",
         f"[0:v]{NORM_V},trim=duration={CARD_HOLD},setpts=PTS-STARTPTS[v];"
         f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{CARD_HOLD},asetpts=PTS-STARTPTS[a]",
         "-map", "[v]", "-map", "[a]", "-t", str(CARD_HOLD), *PRESET, str(out)])


def norm(src: Path, out: Path) -> None:
    run(["ffmpeg", "-y", "-i", str(src),
         "-filter_complex",
         f"[0:v]{NORM_V},setpts=PTS-STARTPTS[v];"
         "[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a]",
         "-map", "[v]", "-map", "[a]", *PRESET, str(out)])


def join(base: Path, incoming: Path, out: Path) -> None:
    off = vdur(base)
    run(["ffmpeg", "-y", "-i", str(base), "-i", str(incoming),
         "-filter_complex",
         f"[0:v]format=yuv420p,fps=30,setsar=1,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={FADE}[v0h];"
         f"[1:v]format=yuv420p,fps=30,setsar=1,setpts=PTS-STARTPTS[v1];"
         f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];"
         f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS,afade=t=in:st=0:d={FADE}[a1];"
         f"[v0h][v1]xfade=transition=fade:duration={FADE}:offset={off:.6f}[v];"
         f"[a0][a1]concat=n=2:v=0:a=1[a]",
         "-map", "[v]", "-map", "[a]", *PRESET, str(out)])


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="dojo-cum-") as tmpdir:
        tmp = Path(tmpdir)
        seq: list[Path] = []

        intro = tmp / "00-intro.mp4"
        norm(S / "01.00.00-what-is-dojo/video/final/CUMULATIVE-through-01.00.01.mp4", intro)
        seq.append(intro)

        c1 = tmp / "c-talk.mp4"; card(S / "02.00.00-stt-talk/after/final/title-card-talk.png", c1); seq.append(c1)
        v1 = tmp / "stt.mp4"; norm(S / "02.00.00-stt-talk/video/final/LOCKED-02-stt.mp4", v1); seq.append(v1)

        c2 = tmp / "c-listen.mp4"; card(S / "02.10.00-tts-listen/after/final/title-card-listen.png", c2); seq.append(c2)
        for name in ("LOCKED-03-woman-arc-opener.mp4", "LOCKED-03-tts-listen.mp4", "LOCKED-03-ears-listen.mp4"):
            p = tmp / name; norm(S / "02.10.00-tts-listen/video/final" / name, p); seq.append(p)

        c3 = tmp / "c-coding.mp4"; card(S / "02.20.00-lane-assist/after/final/title-card-coding-lane-assist.png", c3); seq.append(c3)
        v3 = tmp / "lane.mp4"; norm(S / "02.20.00-lane-assist/video/final/LOCKED-lane-assist.mp4", v3); seq.append(v3)

        c4 = tmp / "c-multi.mp4"; card(S / "02.30.00-more-than-coding/after/final/title-card-multimedia-powerhouse.png", c4); seq.append(c4)
        v4 = tmp / "mtc.mp4"; norm(S / "02.30.00-more-than-coding/video/final/LOCKED-02.30-more-than-coding.mp4", v4); seq.append(v4)

        c5 = tmp / "c-fashion.mp4"; card(S / "03.00.00-tryon/after/final/title-card-fashion-tryon.png", c5); seq.append(c5)
        v5 = tmp / "tryon.mp4"; norm(S / "03.00.00-tryon/video/final/LOCKED-03-tryon.mp4", v5); seq.append(v5)

        c6 = tmp / "c-arch.mp4"; card(S / "04.00.00-architecture-hq/after/final/title-card-architecture.png", c6); seq.append(c6)
        v6 = tmp / "arch.mp4"; norm(S / "04.00.00-architecture-hq/video/final/LOCKED-04-architecture.mp4", v6); seq.append(v6)

        c7 = tmp / "c-combine.mp4"; card(S / "05.00.00-dojox-combine/after/final/title-card-product-combine.png", c7); seq.append(c7)
        v7 = tmp / "combine.mp4"; norm(S / "05.00.00-dojox-combine/video/final/LOCKED-05-product-combine.mp4", v7); seq.append(v7)

        # coffee master already begins with its own BRANDING card
        v8 = tmp / "coffee.mp4"; norm(S / "06.00.00-dojox-coffee/video/final/LOCKED-06-coffee.mp4", v8); seq.append(v8)

        # perfume master already begins with its own STILL LIFE card
        v9 = tmp / "perfume.mp4"; norm(S / "07.00.00-dojox-perfume/video/final/LOCKED-07-perfume.mp4", v9); seq.append(v9)

        # promo master already begins with its own PROMO card
        v10 = tmp / "promo.mp4"; norm(S / "09.00.00-promo-motion/video/final/LOCKED-09-promo.mp4", v10); seq.append(v10)

        # lipsync master already begins with its own LIP SYNC card
        v11 = tmp / "lipsync.mp4"; norm(S / "09.10.00-lipsync/video/final/LOCKED-09.10-lipsync.mp4", v11); seq.append(v11)

        # characters master already begins with its own CHARACTERS card
        v12 = tmp / "characters.mp4"; norm(S / "12.00.00-character-life/video/final/LOCKED-12-characters.mp4", v12); seq.append(v12)

        # multilingual master already begins with its own LANGUAGES card + VO
        v13 = tmp / "multilingual.mp4"; norm(S / "13.00.00-multilingual/video/final/LOCKED-13-multilingual.mp4", v13); seq.append(v13)

        # diagrams+equations master already begins with its own DIAGRAMS card
        v14 = tmp / "diagrams.mp4"; norm(S / "13.10.00-diagrams-equations/video/final/LOCKED-13.10-diagrams-equations.mp4", v14); seq.append(v14)

        # kids tutor master already begins with its own TEACH SAFELY card + VO
        v15 = tmp / "kids.mp4"; norm(S / "14.00.00-kids-tutor/video/final/LOCKED-14-kids-tutor.mp4", v15); seq.append(v15)

        # finale: card -> montage -> torii splash (last frame of the reel)
        v16 = tmp / "finale.mp4"; norm(S / "15.00.00-final/video/final/LOCKED-15-final.mp4", v16); seq.append(v16)

        cur = seq[0]
        for i, nxt in enumerate(seq[1:], 1):
            out = tmp / f"chain-{i:02d}.mp4"
            print(f"join {i:02d}: +{nxt.name}")
            join(cur, nxt, out)
            cur = out

        shutil.copy2(cur, OUT)

    print(f"OUT {OUT} {dur(OUT):.3f}s")


if __name__ == "__main__":
    main()
