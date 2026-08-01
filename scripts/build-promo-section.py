#!/usr/bin/env python3
"""Build the promo motion section: PROMO card -> source still (VO) -> promo video."""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "public/sections/09.00.00-promo-motion"
OUT = SEC / "video/final/LOCKED-09-promo.mp4"

CARD = SEC / "after/final/title-card-promo-motion.png"
STILL = SEC / "before/01-headphones-still.jpg"
PROMO = SEC / "video/01-headphones-promo.mp4"
VO = SEC / "audio/final/promo-eve-vo.mp3"

CARD_HOLD = 1.500
PAD_IN = 0.250
PAD_OUT = 1.000   # VO fully lands before the promo music comes in
FADE = 0.300

SLOWMO_TAIL = 1.000    # last second of source
SLOWMO_FACTOR = 2.0    # half speed
MUSIC_TAPER = 1.600    # fade music out over the slowed tail

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
    for p in (CARD, STILL, PROMO, VO):
        if not p.exists():
            raise SystemExit(f"missing: {p}")

    vo_d = dur(VO)
    still_hold = PAD_IN + vo_d + PAD_OUT
    stills_end = CARD_HOLD + still_hold
    delay = int((CARD_HOLD + PAD_IN) * 1000)
    print(f"VO={vo_d:.3f} card={CARD_HOLD} still={still_hold:.3f} end={stills_end:.3f}")

    with tempfile.TemporaryDirectory(prefix="dojo-promo-") as td:
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

        # Promo with slow-motion tail + music taper at the end
        promo_d = dur(PROMO)
        tail_start = max(0.0, promo_d - SLOWMO_TAIL)
        tail_out = SLOWMO_TAIL * SLOWMO_FACTOR
        promo = tmp / "promo.mp4"
        run([
            "ffmpeg", "-y", "-i", str(PROMO),
            "-filter_complex",
            f"[0:v]{NORM_V},setpts=PTS-STARTPTS,trim=0:{tail_start:.3f},setpts=PTS-STARTPTS[vh];"
            f"[0:v]{NORM_V},setpts=PTS-STARTPTS,trim={tail_start:.3f}:{promo_d:.3f},"
            f"setpts=PTS-STARTPTS,setpts={SLOWMO_FACTOR}*PTS,"
            f"minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1[vt];"
            f"[vh][vt]concat=n=2:v=1:a=0[v];"
            f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS,"
            f"atrim=0:{tail_start:.3f},asetpts=PTS-STARTPTS[ah];"
            f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS,"
            f"atrim={tail_start:.3f}:{promo_d:.3f},asetpts=PTS-STARTPTS,"
            f"atempo={1.0 / SLOWMO_FACTOR:.4f}[at];"
            f"[ah][at]concat=n=2:v=0:a=1,"
            f"afade=t=out:st={tail_start + tail_out - MUSIC_TAPER:.3f}:d={MUSIC_TAPER}[a]",
            "-map", "[v]", "-map", "[a]", *ENC, str(promo),
        ])

        run([
            "ffmpeg", "-y", "-i", str(stills), "-i", str(promo),
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
