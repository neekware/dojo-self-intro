#!/usr/bin/env python3
"""Butter-smooth zooms via per-frame crop (no zoompan jitter) + rebuild sequence."""

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
GIRL = FINAL / "01-girl-behind-to-side.mp4"
FPS = 24
XFADE = 0.7
OUT_W, OUT_H = 1280, 720


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


def smoothstep(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)


def ease_in_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 4 * t * t * t
    return 1 - pow(-2 * t + 2, 3) / 2


def render_smooth_zoom(
    src: Path,
    dest_mp4: Path,
    duration: float,
    *,
    z0: float = 1.0,
    z1: float = 1.48,
    # focus as fraction of image (0..1) — where zoom aims
    focus_x: float = 0.55,
    focus_y: float = 0.72,
) -> Path:
    im = Image.open(src).convert("RGB")
    # work at high res for clean crops
    base = im
    if base.width < 1920:
        scale = 1920 / base.width
        base = base.resize(
            (int(base.width * scale), int(base.height * scale)),
            Image.Resampling.LANCZOS,
        )

    iw, ih = base.size
    n = int(round(duration * FPS))
    tmp = Path(tempfile.mkdtemp(prefix="smooth-zoom-"))
    try:
        for i in range(n):
            t = ease_in_out_cubic(i / max(1, n - 1))
            z = z0 + (z1 - z0) * t
            # visible window size in source pixels
            vw = iw / z
            vh = ih / z
            # keep aspect of output
            target_aspect = OUT_W / OUT_H
            win_aspect = vw / vh
            if win_aspect > target_aspect:
                vw = vh * target_aspect
            else:
                vh = vw / target_aspect

            cx = focus_x * iw
            cy = focus_y * ih
            # as we zoom, ease focus slightly deeper into target
            cx = cx + (focus_x - 0.5) * iw * 0.08 * t
            cy = cy + (focus_y - 0.5) * ih * 0.10 * t

            left = cx - vw / 2
            top = cy - vh / 2
            # clamp
            left = max(0.0, min(left, iw - vw))
            top = max(0.0, min(top, ih - vh))
            right = left + vw
            bottom = top + vh

            crop = base.crop((int(left), int(top), int(math.ceil(right)), int(math.ceil(bottom))))
            frame = crop.resize((OUT_W, OUT_H), Image.Resampling.LANCZOS)
            frame.save(tmp / f"f{i:05d}.png")

        # encode
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
                str(dest_mp4),
            ]
        )
        print("smooth zoom", dest_mp4, probe(dest_mp4))
        return dest_mp4
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def mux(video: Path, audio: Path, dest: Path) -> Path:
    vdur = probe(video)
    adur = probe(audio)
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
            "copy",
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
    # copy may fail if need remux with -shortest etc; re-encode video if needed
    if not dest.exists() or dest.stat().st_size < 1000:
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
    print("mux", dest.name, f"delay_ms={delay}")
    return dest


def rebuild(eq: Path, ac: Path) -> None:
    paths = [GIRL, eq, ac]
    tmp = Path(tempfile.mkdtemp(prefix="kids-sm-"))
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
    eq_raw = SEC / "video/02-equation-zoom-smooth.mp4"
    ac_raw = SEC / "video/03-access-zoom-smooth.mp4"

    # Equation: gentle center zoom
    a_eq = SEC / "audio/01-quadratic-explain.mp3"
    eq_dur = max(12.0, probe(a_eq) + 1.0)
    render_smooth_zoom(
        SEC / "after/01-equation-full-16x9.jpg",
        eq_raw,
        eq_dur,
        z0=1.0,
        z1=1.42,
        focus_x=0.50,
        focus_y=0.48,
    )
    eq = mux(eq_raw, a_eq, FINAL / "02-equation-with-vo.mp4")

    # Access control: aim lower-center toward Kids 7-12 row
    a_ac = SEC / "audio/02-parental-control-line.mp3"
    ac_dur = max(10.0, probe(a_ac) + 0.8)
    render_smooth_zoom(
        SEC / "after/02-access-control-full-16x9.jpg",
        ac_raw,
        ac_dur,
        z0=1.0,
        z1=1.55,
        focus_x=0.58,
        focus_y=0.78,
    )
    ac = mux(ac_raw, a_ac, FINAL / "03-access-with-vo.mp4")

    rebuild(eq, ac)


if __name__ == "__main__":
    main()
