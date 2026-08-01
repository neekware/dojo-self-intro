#!/usr/bin/env python3
"""Remux locked FA VO (centered) and rebuild blur-dissolve master."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/13.00.00-multilingual"
VID = SEC / "video/01-heavenly-hill-alive.mp4"
AUDIO = SEC / "audio/06-fa.mp3"
OVERLAY = SEC / "after/subtitles/overlays/overlay-fa.png"
OUT_FA = SEC / "video/lang/heavenly-fa-sub.mp4"
MASTER = SEC / "video/04-multilingual-one-blur-switch.mp4"
TMP = SEC / "video/.tmp-blur"
ORDER = ["en", "es", "fr", "ja", "zh", "fa", "ar", "hi"]
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


def mux_fa() -> None:
    vdur = probe(VID)
    adur = probe(AUDIO)
    delay_ms = max(0, int(((vdur - adur) / 2) * 1000))
    fc = (
        f"[0:v][1:v]overlay=0:0:format=auto[v];"
        f"[2:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"adelay={delay_ms}|{delay_ms},apad=whole_dur={vdur}[a]"
    )
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(VID),
            "-i",
            str(OVERLAY),
            "-i",
            str(AUDIO),
            "-filter_complex",
            fc,
            "-map",
            "[v]",
            "-map",
            "[a]",
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
            "-t",
            str(vdur),
            "-movflags",
            "+faststart",
            str(OUT_FA),
        ]
    )
    print("FA", OUT_FA, "delay_ms", delay_ms, "dur", probe(OUT_FA))


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


def build_master() -> None:
    TMP.mkdir(parents=True, exist_ok=True)
    paths = [SEC / "video/lang" / f"heavenly-{c}-sub.mp4" for c in ORDER]
    for p in paths:
        assert p.exists(), p

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
        vchain += (
            f"[v{prev}][{i}:v]xfade=transition=fadeblack:duration={XFADE}:offset={off:.3f}[v{i}];"
        )
        achain += f"[a{prev}][{i}:a]acrossfade=d={XFADE}:c1=tri:c2=tri[a{i}];"

    last = n - 1
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            *inputs,
            "-filter_complex",
            vchain + achain,
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
    )
    print("MASTER", MASTER, probe(MASTER))
    shutil.rmtree(TMP, ignore_errors=True)


def main() -> None:
    mux_fa()
    build_master()


if __name__ == "__main__":
    main()
