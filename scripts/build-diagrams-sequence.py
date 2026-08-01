#!/usr/bin/env python3
"""Animate diagram stills with smooth Ken Burns + crossfade montage + VO."""

from __future__ import annotations

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/13.10.00-diagrams-equations"
BEFORE = SEC / "before"
VID = SEC / "video"
FINAL = VID / "final"
AUDIO_SRC = Path(
    "/Users/val/.dojo/workspace/artifacts/ads-b9196c98/audio-gen/diagrams-native-vo-ms96oe8a.mp3"
)
AUDIO = SEC / "audio/01-diagrams-native-vo.mp3"
FPS = 24
OUT_W, OUT_H = 1280, 720
CLIP_SEC = 4.2
XFADE = 0.75

# Order: software diagrams → pie → investor chart
ORDER = [
    ("01-state-auth-full.jpg", 1.0, 1.12, 0.50, 0.48),  # complex state
    ("02-state-auth-simple.jpg", 1.0, 1.14, 0.50, 0.45),
    ("04-flow-services.jpg", 1.0, 1.12, 0.52, 0.50),
    ("03-pie-dev-day.jpg", 1.0, 1.15, 0.48, 0.50),
    ("05-line-tesla-google.jpg", 1.0, 1.12, 0.55, 0.52),
]


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


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def ken_burns(
    src: Path,
    dest: Path,
    duration: float,
    z0: float,
    z1: float,
    fx: float,
    fy: float,
) -> None:
    im = Image.open(src).convert("RGB")
    # fit to 16:9 canvas first
    W, H = 1920, 1080
    canvas = Image.new("RGB", (W, H), (8, 10, 14))
    scale = min(W / im.width, H / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im2 = im.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas.paste(im2, ((W - nw) // 2, (H - nh) // 2))
    im = canvas
    iw, ih = im.size
    n = int(round(duration * FPS))
    tmp = Path(tempfile.mkdtemp(prefix="diag-kb-"))
    try:
        for i in range(n):
            t = ease(i / max(1, n - 1))
            z = z0 + (z1 - z0) * t
            vw, vh = iw / z, ih / z
            aspect = OUT_W / OUT_H
            if vw / vh > aspect:
                vw = vh * aspect
            else:
                vh = vw / aspect
            # slight drift toward focal point
            cx = iw * (0.5 + (fx - 0.5) * t)
            cy = ih * (0.5 + (fy - 0.5) * t)
            left = max(0.0, min(cx - vw / 2, iw - vw))
            top = max(0.0, min(cy - vh / 2, ih - vh))
            crop = im.crop(
                (int(left), int(top), int(math.ceil(left + vw)), int(math.ceil(top + vh)))
            )
            crop.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS).save(tmp / f"f{i:05d}.png")
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                "-framerate",
                str(FPS),
                "-i",
                str(tmp / "f%05d.png"),
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "16",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                str(dest),
            ]
        )
        print("clip", dest.name, probe(dest))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def xfade(paths: list[Path], dest: Path) -> None:
    tmp = Path(tempfile.mkdtemp(prefix="diag-xf-"))
    try:
        norms = []
        for i, p in enumerate(paths):
            n = tmp / f"n{i}.mp4"
            # silent stereo bed
            subprocess.check_call(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(p),
                    "-f",
                    "lavfi",
                    "-i",
                    "anullsrc=channel_layout=stereo:sample_rate=48000",
                    "-shortest",
                    "-vf",
                    "fps=24,format=yuv420p",
                    "-map",
                    "0:v:0",
                    "-map",
                    "1:a:0",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "16",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-ar",
                    "48000",
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
        silent = tmp / "silent.mp4"
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
                "16",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-movflags",
                "+faststart",
                str(silent),
            ]
        )
        # mux VO centered over full montage
        vdur = probe(silent)
        adur = probe(AUDIO)
        delay = max(0, int(((vdur - adur) / 2) * 1000))
        # if VO longer, pad video
        src = silent
        if adur + 0.4 > vdur:
            pad = adur + 0.6 - vdur
            padded = tmp / "pad.mp4"
            subprocess.check_call(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(silent),
                    "-vf",
                    f"tpad=stop_mode=clone:stop_duration={pad:.3f}",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "16",
                    "-c:a",
                    "copy",
                    "-movflags",
                    "+faststart",
                    str(padded),
                ]
            )
            src = padded
            vdur = probe(src)
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
                str(src),
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
                "16",
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
        print("MASTER", dest, probe(dest), "vo_delay_ms", delay)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    FINAL.mkdir(parents=True, exist_ok=True)
    (SEC / "audio").mkdir(parents=True, exist_ok=True)
    shutil.copy2(AUDIO_SRC, AUDIO)
    shutil.copy2(AUDIO, SEC / "audio/final/diagrams-native-vo.mp3")

    clips = []
    for i, (name, z0, z1, fx, fy) in enumerate(ORDER, 1):
        src = BEFORE / name
        dest = VID / f"clip-{i:02d}-{Path(name).stem}.mp4"
        ken_burns(src, dest, CLIP_SEC, z0, z1, fx, fy)
        shutil.copy2(dest, FINAL / dest.name)
        clips.append(dest)

    master = FINAL / "diagrams-sequence.mp4"
    xfade(clips, master)
    shutil.copy2(master, VID / "04-diagrams-sequence.mp4")
    shutil.copy2(master, FINAL / "LOCKED-diagrams-sequence.mp4")


if __name__ == "__main__":
    main()
