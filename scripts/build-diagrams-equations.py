#!/usr/bin/env python3
"""Build the DIAGRAMS + EQUATIONS section.

Card -> five diagram/chart stills -> two equation stills, ending on the
quadratic formula. One continuous Eve VO spans the whole body.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "public/sections/13.10.00-diagrams-equations"
OUT = SEC / "video/final/LOCKED-13.10-diagrams-equations.mp4"

CARD = SEC / "after/final/title-card-diagrams.png"
VO = SEC / "audio/final/diagrams-equations-vo.mp3"

# (file, relative weight) — ends on the quadratic formula
BEATS = [
    ("before/01-state-auth-full.jpg", 1.0),
    ("before/02-state-auth-simple.jpg", 0.9),
    ("before/04-flow-services.jpg", 1.0),
    ("before/03-pie-dev-day.jpg", 0.9),
    ("before/05-line-tesla-google.jpg", 1.0),
    ("before/06-gravity-light.png", 1.5),
    ("before/07-quadratic.png", 1.6),
]

CARD_HOLD = 1.500
PAD_IN = 0.250
PAD_OUT = 0.600
XFADE = 0.350   # gentle dissolve between stills

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
    beats = [(SEC / rel, w) for rel, w in BEATS]
    for p, _ in beats:
        if not p.exists():
            raise SystemExit(f"missing beat: {p}")
    for p in (CARD, VO):
        if not p.exists():
            raise SystemExit(f"missing: {p}")

    vo_d = dur(VO)
    body = PAD_IN + vo_d + PAD_OUT
    total = CARD_HOLD + body
    wsum = sum(w for _, w in beats)

    # Each still needs XFADE extra so dissolves overlap without shortening the beat.
    holds = [body * w / wsum + XFADE for _, w in beats]
    print(f"VO={vo_d:.3f} body={body:.3f} total={total:.3f}")
    for (p, _), h in zip(beats, holds):
        print(f"  {h:5.3f}s  {p.name}")

    with tempfile.TemporaryDirectory(prefix="dojo-diagq-") as td:
        tmp = Path(td)

        inputs: list[str] = ["-loop", "1", "-t", f"{CARD_HOLD + XFADE:.3f}", "-i", str(CARD)]
        for (path, _), hold in zip(beats, holds):
            inputs += ["-loop", "1", "-t", f"{hold:.3f}", "-i", str(path)]
        inputs += ["-i", str(VO)]

        n = len(beats) + 1  # card + stills
        parts = "".join(f"[{i}:v]{NORM_V},setpts=PTS-STARTPTS[s{i}];" for i in range(n))

        # chain xfades
        chain = ""
        prev = "s0"
        offset = CARD_HOLD
        for i in range(1, n):
            label = f"x{i}"
            chain += (f"[{prev}][s{i}]xfade=transition=fade:"
                      f"duration={XFADE}:offset={offset:.3f}[{label}];")
            offset += holds[i - 1] - XFADE
            prev = label

        delay = int((CARD_HOLD + PAD_IN) * 1000)
        run([
            "ffmpeg", "-y", *inputs,
            "-filter_complex",
            f"{parts}{chain}[{prev}]trim=0:{total:.3f},setpts=PTS-STARTPTS[v];"
            f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"adelay={delay}|{delay},apad,atrim=0:{total:.3f},asetpts=PTS-STARTPTS[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", *ENC, str(OUT),
        ])

    print(f"OUT {OUT} {dur(OUT):.3f}s")


if __name__ == "__main__":
    main()
