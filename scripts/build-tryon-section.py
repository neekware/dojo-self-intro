#!/usr/bin/env python3
"""Build the Virtual Try-On section: woman -> dress -> fit -> walk.

Stills carry one continuous Eve VO; the walk clip follows with a 300ms
incoming fade. Intermediates render in a temp dir and are auto-removed.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "public/sections/03.00.00-tryon"
OUT = SEC / "video/final/LOCKED-03-tryon.mp4"

WOMAN = SEC / "before/01-base-green-white-screen.png"
DRESS = SEC / "before/02-dress-garment-only.png"
FIT = SEC / "after/03-evening-dress-emerald.png"
WALK = SEC / "video/01-dress-walk.mp4"
VO = SEC / "audio/final/tryon-eve-vo.mp3"

PAD_IN = 0.250
PAD_OUT = 0.400
FADE = 0.300

# Beat lengths inside the stills block (sum must equal stills duration)
WOMAN_HOLD = 2.300
DRESS_HOLD = 2.100

# Slow-motion tail on the walk clip
SLOWMO_TAIL = 1.500   # seconds of source to slow
SLOWMO_FACTOR = 2.0   # 2.0 = half speed

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
    vo_d = dur(VO)
    stills_end = PAD_IN + vo_d + PAD_OUT
    fit_hold = stills_end - WOMAN_HOLD - DRESS_HOLD
    if fit_hold < 0.8:
        raise SystemExit(f"fit hold too short: {fit_hold:.3f}")
    print(f"VO={vo_d:.3f} stills={stills_end:.3f} "
          f"woman={WOMAN_HOLD} dress={DRESS_HOLD} fit={fit_hold:.3f}")

    with tempfile.TemporaryDirectory(prefix="dojo-tryon-") as td:
        tmp = Path(td)
        stills = tmp / "stills.mp4"
        delay = int(PAD_IN * 1000)
        run([
            "ffmpeg", "-y",
            "-loop", "1", "-t", f"{WOMAN_HOLD:.3f}", "-i", str(WOMAN),
            "-loop", "1", "-t", f"{DRESS_HOLD:.3f}", "-i", str(DRESS),
            "-loop", "1", "-t", f"{fit_hold:.3f}", "-i", str(FIT),
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

        # Walk with a slow-motion tail: last SLOWMO_TAIL seconds stretched by SLOWMO_FACTOR
        walk_d = dur(WALK)
        tail_start = max(0.0, walk_d - SLOWMO_TAIL)
        walk = tmp / "walk.mp4"
        run([
            "ffmpeg", "-y", "-i", str(WALK),
            "-filter_complex",
            # head: normal speed
            f"[0:v]{NORM_V},setpts=PTS-STARTPTS,trim=0:{tail_start:.3f},setpts=PTS-STARTPTS[vh];"
            # tail: slow motion with motion interpolation
            f"[0:v]{NORM_V},setpts=PTS-STARTPTS,trim={tail_start:.3f}:{walk_d:.3f},setpts=PTS-STARTPTS,"
            f"setpts={SLOWMO_FACTOR}*PTS,"
            f"minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1[vt];"
            f"[vh][vt]concat=n=2:v=1:a=0[v];"
            # audio: head normal, tail slowed to match
            f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS,"
            f"atrim=0:{tail_start:.3f},asetpts=PTS-STARTPTS[ah];"
            f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS,"
            f"atrim={tail_start:.3f}:{walk_d:.3f},asetpts=PTS-STARTPTS,"
            f"atempo={1.0 / SLOWMO_FACTOR:.4f},afade=t=out:st={SLOWMO_TAIL * SLOWMO_FACTOR - 0.5:.3f}:d=0.5[at];"
            f"[ah][at]concat=n=2:v=0:a=1[a]",
            "-map", "[v]", "-map", "[a]", *ENC, str(walk),
        ])

        run([
            "ffmpeg", "-y", "-i", str(stills), "-i", str(walk),
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
