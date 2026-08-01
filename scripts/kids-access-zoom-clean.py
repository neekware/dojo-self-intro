#!/usr/bin/env python3
"""Clean mechanical zoom on real Access Control UI + rebuild kids sequence."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/14.00.00-kids-tutor"
SRC = SEC / "after/02-access-control-full-16x9.jpg"
RAW = SEC / "video/03-access-zoom-clean.mp4"
AUDIO = SEC / "audio/02-parental-control-line.mp3"
GIRL = SEC / "video/final/01-girl-behind-to-side.mp4"
EQ = SEC / "video/final/02-equation-with-vo.mp4"
FINAL = SEC / "video/final"
XFADE = 0.7


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


def make_zoom() -> None:
    # 10s @ 24fps — slow zoom toward Audience / Kids 7-12 (lower center)
    vf = (
        "scale=1920:1080,"
        "zoompan=z='min(1.0+0.0023*on\\,1.55)'"
        ":x='iw/2-(iw/zoom/2)+20'"
        ":y='ih/2-(ih/zoom/2)+on*0.45'"
        ":d=1:s=1280x720:fps=24,"
        "format=yuv420p"
    )
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(SRC),
            "-vf",
            vf,
            "-t",
            "10",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(RAW),
        ]
    )
    print("zoom", RAW, probe(RAW))


def mux_audio() -> Path:
    dest = FINAL / "03-access-with-vo.mp4"
    vdur = probe(RAW)
    adur = probe(AUDIO)
    delay = max(0, int(((vdur - adur) / 2) * 1000))
    fc = (
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"adelay={delay}|{delay},apad=whole_dur={vdur}[a]"
    )
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(RAW),
            "-i",
            str(AUDIO),
            "-filter_complex",
            fc,
            "-map",
            "0:v:0",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "17",
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
            str(dest),
        ]
    )
    print("mux", dest, f"v={vdur:.2f} a={adur:.2f} delay={delay}")
    return dest


def rebuild_sequence(ac: Path) -> None:
    paths = [GIRL, EQ, ac]
    tmp = Path(tempfile.mkdtemp(prefix="kids-fix-"))
    try:
        norms = []
        for i, p in enumerate(paths):
            n = tmp / f"n{i}.mp4"
            subprocess.check_call(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(p),
                    "-vf",
                    "fps=24,scale=1280:720:force_original_aspect_ratio=decrease,"
                    "pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "17",
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
                    str(n),
                ]
            )
            norms.append(n)

        durs = [probe(p) for p in norms]
        offsets = [0.0]
        for i in range(1, len(norms)):
            offsets.append(offsets[-1] + durs[i - 1] - XFADE)

        inputs: list[str] = []
        for p in norms:
            inputs += ["-i", str(p)]
        v = "[0:v]null[v0];"
        a = "[0:a]anull[a0];"
        for i in range(1, len(norms)):
            v += f"[v{i-1}][{i}:v]xfade=transition=fade:duration={XFADE}:offset={offsets[i]:.4f}[v{i}];"
            a += f"[a{i-1}][{i}:a]acrossfade=d={XFADE}:c1=tri:c2=tri[a{i}];"
        last = len(norms) - 1
        dest = FINAL / "kids-tutor-sequence.mp4"
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                *inputs,
                "-filter_complex",
                v + a,
                "-map",
                f"[v{last}]",
                "-map",
                f"[a{last}]",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "17",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-movflags",
                "+faststart",
                str(dest),
            ]
        )
        shutil.copy2(dest, SEC / "video/04-kids-tutor-sequence.mp4")
        print("MASTER", dest, probe(dest))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    make_zoom()
    ac = mux_audio()
    rebuild_sequence(ac)


if __name__ == "__main__":
    main()
