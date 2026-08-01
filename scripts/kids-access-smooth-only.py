#!/usr/bin/env python3
"""Smooth Access Control zoom only (real UI) + mux VO + rebuild sequence with user's equation clip."""

from __future__ import annotations

import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/14.00.00-kids-tutor"
FINAL = SEC / "video/final"
FPS = 24
OUT_W, OUT_H = 1280, 720
XFADE = 0.7

# User-approved equation clip
EQ_SRC = Path(
    "/Users/val/.dojo/workspace/artifacts/ads-b9196c98/video-gen/"
    "kids-equation-zoom-video_0ms962y7d_992c7515.mp4"
)
EQ_AUDIO = SEC / "audio/01-quadratic-explain.mp3"
AC_STILL = SEC / "after/02-access-control-full-16x9.jpg"
AC_AUDIO = SEC / "audio/02-parental-control-line.mp3"
GIRL = FINAL / "01-girl-behind-to-side.mp4"


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


def smooth_zoom(src: Path, dest: Path, duration: float) -> None:
    im = Image.open(src).convert("RGB")
    if im.width < 1920:
        s = 1920 / im.width
        im = im.resize((int(im.width * s), int(im.height * s)), Image.Resampling.LANCZOS)
    iw, ih = im.size
    n = int(round(duration * FPS))
    tmp = Path(tempfile.mkdtemp(prefix="ac-sm-"))
    try:
        z0, z1 = 1.0, 1.52
        fx, fy = 0.58, 0.78  # Kids 7-12 area
        for i in range(n):
            t = ease(i / max(1, n - 1))
            z = z0 + (z1 - z0) * t
            vw, vh = iw / z, ih / z
            aspect = OUT_W / OUT_H
            if vw / vh > aspect:
                vw = vh * aspect
            else:
                vh = vw / aspect
            cx = fx * iw + (fx - 0.5) * iw * 0.06 * t
            cy = fy * ih + (fy - 0.5) * ih * 0.08 * t
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
        print("ac zoom", dest, probe(dest))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def mux(video: Path, audio: Path, dest: Path) -> Path:
    vdur, adur = probe(video), probe(audio)
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
            str(video),
            "-i",
            str(audio),
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
    print("mux", dest.name, f"v={vdur:.2f} a={adur:.2f} delay={delay}")
    return dest


def rebuild(eq: Path, ac: Path) -> None:
    paths = [GIRL, eq, ac]
    tmp = Path(tempfile.mkdtemp(prefix="kids-rb-"))
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
                    "16",
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
        v, a = "[0:v]null[v0];", "[0:a]anull[a0];"
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
                "16",
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
    FINAL.mkdir(parents=True, exist_ok=True)
    # equation: user clip + centered VO (extend if needed by padding end freeze)
    eq_raw = SEC / "video/02-equation-user.mp4"
    shutil.copy2(EQ_SRC, eq_raw)
    # if VO longer than video, pad last frame
    vdur, adur = probe(eq_raw), probe(EQ_AUDIO)
    if adur + 0.6 > vdur:
        pad = adur + 0.8 - vdur
        padded = SEC / "video/02-equation-user-padded.mp4"
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(eq_raw),
                "-vf",
                f"tpad=stop_mode=clone:stop_duration={pad:.3f}",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "16",
                "-an",
                "-movflags",
                "+faststart",
                str(padded),
            ]
        )
        eq_raw = padded
    eq = mux(eq_raw, EQ_AUDIO, FINAL / "02-equation-with-vo.mp4")

    # access: smooth real-UI zoom only
    ac_raw = SEC / "video/03-access-zoom-smooth.mp4"
    ac_dur = max(10.0, probe(AC_AUDIO) + 0.8)
    smooth_zoom(AC_STILL, ac_raw, ac_dur)
    ac = mux(ac_raw, AC_AUDIO, FINAL / "03-access-with-vo.mp4")

    rebuild(eq, ac)


if __name__ == "__main__":
    main()
