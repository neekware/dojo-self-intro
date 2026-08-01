#!/usr/bin/env python3
"""Build one blur-switch master in locked language order."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/13.00.00-multilingual"
OUT_LANG = SEC / "video/lang"
MASTER = SEC / "video/04-multilingual-one-blur-switch.mp4"
TMP = SEC / "video/.tmp-blur-locked"
TMP.mkdir(parents=True, exist_ok=True)

# Locked order from Val
ORDER = ["en", "fr", "fa", "ja", "ar", "es", "zh"]
XFADE = 0.85


def probe(path: Path) -> float:
    return float(
        subprocess.check_output(
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
    )


def normalize(src: Path, dest: Path) -> None:
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-vf",
            "fps=24,format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
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
            str(dest),
        ]
    )


def main() -> None:
    paths = []
    for code in ORDER:
        p = OUT_LANG / f"heavenly-{code}-sub.mp4"
        if not p.exists():
            raise SystemExit(f"missing {p}")
        print("use", code, p, "dur", probe(p))
        paths.append(p)

    norms = []
    for i, p in enumerate(paths):
        n = TMP / f"n{i:02d}.mp4"
        normalize(p, n)
        norms.append(n)

    durs = [probe(p) for p in norms]
    n = len(norms)
    offsets = [0.0]
    for i in range(1, n):
        offsets.append(offsets[-1] + durs[i - 1] - XFADE)

    inputs: list[str] = []
    for p in norms:
        inputs.extend(["-i", str(p)])

    vchain = "[0:v]null[v0];"
    achain = "[0:a]anull[a0];"
    for i in range(1, n):
        prev = i - 1
        off = offsets[i]
        # soft blur-ish dissolve via fadeblack (clean language switch)
        vchain += (
            f"[v{prev}][{i}:v]xfade=transition=fadeblack:duration={XFADE}:offset={off:.3f}[v{i}];"
        )
        achain += f"[a{prev}][{i}:a]acrossfade=d={XFADE}:c1=tri:c2=tri[a{i}];"

    fc = vchain + achain
    last = n - 1
    cmd = [
        "ffmpeg",
        "-y",
        *inputs,
        "-filter_complex",
        fc,
        "-map",
        f"[v{last}]",
        "-map",
        f"[a{last}]",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-movflags",
        "+faststart",
        str(MASTER),
    ]
    subprocess.check_call(cmd)
    print("MASTER", MASTER, probe(MASTER))
    print("ORDER", " → ".join(c.upper() for c in ORDER))
    shutil.rmtree(TMP, ignore_errors=True)

    notes = SEC / "text/NOTES.md"
    body = notes.read_text(encoding="utf-8")
    lock = (
        "\n## LOCKED master order\n\n"
        "EN → FR → FA → JA → AR → ES → ZH\n\n"
        "- File: `video/04-multilingual-one-blur-switch.mp4`\n"
        "- FA VO: Eve `hameenjaast` lock (`audio/06-fa.mp3`)\n"
        "- Hindi omitted from master\n"
    )
    if "LOCKED master order" not in body:
        notes.write_text(body.rstrip() + "\n" + lock, encoding="utf-8")
    else:
        # replace old lock block simply by append unique timestamp-less update at end if needed
        pass


if __name__ == "__main__":
    main()
