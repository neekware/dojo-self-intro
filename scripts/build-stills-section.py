#!/usr/bin/env python3
"""Generic stills-with-VO section builder.

Usage:
    python3 scripts/build-stills-section.py <config-name>

Configs live in SECTIONS below: an ordered list of (image, weight) beats plus
the VO path and output master. One continuous Eve VO spans the whole block.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "public/sections"

PAD_IN = 0.250
PAD_OUT = 0.500

NORM_V = ("scale=1920:1080:flags=lanczos:force_original_aspect_ratio=decrease,"
          "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p")
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart"]

CARD_HOLD = 1.500
FADE = 0.300

SECTIONS: dict[str, dict] = {
    "coffee": {
        "dir": S / "06.00.00-dojox-coffee",
        "vo": "audio/final/coffee-eve-vo.mp3",
        "out": "video/final/LOCKED-06-coffee.mp4",
        "card": "after/final/title-card-product-shot-coffee.png",
        "beats": [
            ("before/01-coffee-sample-source.jpg", 1.0),
            ("after/01-coffee-bag-dojox.png", 1.3),
            ("after/02-coffee-hero-styled.png", 2.0),
        ],
    },
    "perfume": {
        "dir": S / "07.00.00-dojox-perfume",
        "vo": "audio/final/perfume-eve-vo.mp3",
        "out": "video/final/LOCKED-07-perfume.mp4",
        "card": "after/final/title-card-product-shot-perfume.png",
        "beats": [
            ("before/01-perfume-sample-source.jpg", 1.0),
            ("after/01-perfume-dojox-hero.png", 2.2),
        ],
    },
}


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def dur(p: Path) -> float:
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)], text=True).strip())


def build(name: str) -> None:
    cfg = SECTIONS[name]
    base: Path = cfg["dir"]
    vo = base / cfg["vo"]
    out = base / cfg["out"]
    out.parent.mkdir(parents=True, exist_ok=True)

    beats = [(base / rel, w) for rel, w in cfg["beats"]]
    for path, _ in beats:
        if not path.exists():
            raise SystemExit(f"missing beat: {path}")
    if not vo.exists():
        raise SystemExit(f"missing VO: {vo}")

    vo_d = dur(vo)
    total = PAD_IN + vo_d + PAD_OUT
    wsum = sum(w for _, w in beats)
    holds = [total * w / wsum for _, w in beats]
    print(f"[{name}] VO={vo_d:.3f} total={total:.3f}")
    for (p, _), h in zip(beats, holds):
        print(f"  {h:5.3f}s  {p.name}")

    card_rel = cfg.get("card")
    card = base / card_rel if card_rel else None
    if card and not card.exists():
        raise SystemExit(f"missing card: {card}")

    # Card leads the section: silent hold, then VO stills fade in over FADE.
    inputs: list[str] = []
    idx = 0
    if card:
        inputs += ["-loop", "1", "-t", f"{CARD_HOLD:.3f}", "-i", str(card)]
        idx = 1
    for (path, _), hold in zip(beats, holds):
        inputs += ["-loop", "1", "-t", f"{hold:.3f}", "-i", str(path)]
    inputs += ["-i", str(vo)]

    n = len(beats)
    vo_idx = idx + n
    delay = int((PAD_IN + (CARD_HOLD if card else 0.0)) * 1000)
    total_out = total + (CARD_HOLD if card else 0.0)

    parts = ""
    if card:
        parts += f"[0:v]{NORM_V},setpts=PTS-STARTPTS[vc];"
    parts += "".join(
        f"[{idx + i}:v]{NORM_V},setpts=PTS-STARTPTS[v{i}];" for i in range(n)
    )
    chain = ("[vc]" if card else "") + "".join(f"[v{i}]" for i in range(n))
    ncat = n + (1 if card else 0)

    run([
        "ffmpeg", "-y", *inputs,
        "-filter_complex",
        f"{parts}{chain}concat=n={ncat}:v=1:a=0[v];"
        f"[{vo_idx}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
        f"adelay={delay}|{delay},apad,atrim=0:{total_out:.3f},asetpts=PTS-STARTPTS[a]",
        "-map", "[v]", "-map", "[a]", "-t", f"{total_out:.3f}", *ENC, str(out),
    ])
    print(f"OUT {out} {dur(out):.3f}s")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in SECTIONS:
        raise SystemExit(f"usage: build-stills-section.py [{'|'.join(SECTIONS)}]")
    build(sys.argv[1])


if __name__ == "__main__":
    main()
