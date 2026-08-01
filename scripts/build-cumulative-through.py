#!/usr/bin/env python3
"""Build cumulative PREVIEW: prepend prior locked standalones through a target.

WORKFLOW LAW
  - Standalone LOCKED-*.mp4 per section = source of truth (edit/swap here).
  - Cumulative CUMULATIVE-through-*.mp4 = preview only ("how does it feel so far?").
  - Final site reel = assemble standalones at the end (not ship mid-chain cumulatives).
  - Changing a middle section = rebuild that standalone + re-assemble final.

SEAMS MUST BE VERY SMOOTH at joins when previewing/assembling.

Usage:
  python3 scripts/build-cumulative-through.py 01.00.00-what-is-dojo --fade 0.25 --tag 01.00.01
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC_ROOT = ROOT / "public/sections"

# Default very slow seam (seconds). Override with --fade.
DEFAULT_FADE = 2.0

# Film-order chain of standalone masters (path relative to section folder).
CHAIN: list[tuple[str, str]] = [
    ("00.00.00-brand", "video/final/LOCKED-00-brand-open.mp4"),
    ("01.00.00-what-is-dojo", "video/final/LOCKED-01-what-is-dojo.mp4"),
    # next majors append here when locked:
    # ("02.00.00-stt-talk", "video/final/LOCKED-02-stt.mp4"),
]


def ver_key(folder: str) -> tuple[int, int, int]:
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)-", folder)
    if not m:
        raise ValueError(folder)
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def probe(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return float(out)


def build_xfade_filter(n: int, durs: list[float], fade: float) -> tuple[str, float]:
    """Build filter_complex for sequential xfade + acrossfade.

    Returns (filter_complex, output_duration).
    """
    if n < 1:
        raise ValueError("need clips")
    if n == 1:
        return "[0:v]format=yuv420p,fps=30,setsar=1[v];[0:a]aformat=sample_rates=48000:channel_layouts=stereo[a]", durs[0]

    # Normalize each input first
    parts: list[str] = []
    for i in range(n):
        parts.append(
            f"[{i}:v]format=yuv420p,fps=30,setsar=1,setpts=PTS-STARTPTS[v{i}];"
            f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]"
        )

    # Running duration of current chain after each xfade
    # After joining clip i into acc: new_dur = prev_dur + durs[i] - fade
    acc_dur = durs[0]
    v_prev = "v0"
    a_prev = "a0"
    for i in range(1, n):
        if durs[i - 1] <= fade + 0.05 or durs[i] <= fade + 0.05:
            raise SystemExit(
                f"fade {fade}s too long for clip lengths "
                f"({durs[i-1]:.3f}s / {durs[i]:.3f}s)"
            )
        # offset = where fade starts on the growing left stream
        offset = acc_dur - fade
        v_out = f"vx{i}"
        a_out = f"ax{i}"
        parts.append(
            f"[{v_prev}][v{i}]xfade=transition=fade:duration={fade:.3f}:offset={offset:.3f}[{v_out}];"
            f"[{a_prev}][a{i}]acrossfade=d={fade:.3f}:c1=tri:c2=tri[{a_out}]"
        )
        acc_dur = acc_dur + durs[i] - fade
        v_prev, a_prev = v_out, a_out

    parts.append(f"[{v_prev}]format=yuv420p[v];[{a_prev}]aformat=sample_rates=48000:channel_layouts=stereo[a]")
    return ";".join(parts), acc_dur


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="section folder e.g. 01.00.00-what-is-dojo")
    ap.add_argument(
        "--fade",
        type=float,
        default=DEFAULT_FADE,
        help=f"slow crossfade seconds at each seam (default {DEFAULT_FADE})",
    )
    ap.add_argument(
        "--tag",
        default="",
        help="optional version tag for output name, e.g. 01.00.01 → CUMULATIVE-through-01.00.01.mp4",
    )
    args = ap.parse_args()
    target = args.target.rstrip("/")
    fade = float(args.fade)
    tkey = ver_key(target)

    clips: list[Path] = []
    for folder, rel in CHAIN:
        if ver_key(folder) > tkey:
            break
        p = SEC_ROOT / folder / rel
        if not p.exists():
            raise SystemExit(f"missing standalone master: {p}")
        clips.append(p)
        if folder == target:
            break
    else:
        if not any(f == target for f, _ in CHAIN):
            raise SystemExit(f"target not in CHAIN yet: {target}")

    if not clips:
        raise SystemExit("no clips")

    durs = [probe(c) for c in clips]
    fc, expected = build_xfade_filter(len(clips), durs, fade)

    out_dir = SEC_ROOT / target / "video/final"
    out_dir.mkdir(parents=True, exist_ok=True)
    maj = target.split("-", 1)[0]
    tag = (args.tag or maj).lstrip("-")
    out = out_dir / f"CUMULATIVE-through-{tag}.mp4"
    work = SEC_ROOT / target / "video/work"
    work.mkdir(parents=True, exist_ok=True)

    cmd = ["ffmpeg", "-y"]
    for c in clips:
        cmd += ["-i", str(c)]
    cmd += [
        "-filter_complex",
        fc,
        "-map",
        "[v]",
        "-map",
        "[a]",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-movflags",
        "+faststart",
        str(out),
    ]
    print("+ fade=", fade, "s")
    subprocess.check_call(cmd)

    total = probe(out)
    print("clips:")
    for c, d in zip(clips, durs):
        print(f"  {d:7.3f}s  {c.relative_to(ROOT)}")
    print(f"fade={fade:.2f}s  expected≈{expected:.3f}s  OUT={total:.3f}s")
    print(out.relative_to(ROOT), out.stat().st_size)
    if abs(total - expected) > 0.35:
        print("WARN duration delta", abs(total - expected), file=sys.stderr)


if __name__ == "__main__":
    main()
