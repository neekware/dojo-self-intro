#!/usr/bin/env python3
"""Smooth end-zoom (no shake) to kill white border; write forward + reverse.

Shake fix: avoid floating zoompan jitter — scale up with a monotonic ease, then
center-crop with *even integer* sizes (trunc), then scale back to 1280x720.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/02.00.00-stt-talk"
SRC = (
    Path.home()
    / ".dojo/workspace/artifacts/ads-b9196c98/video-gen"
    / "code-mic-orbit-into-soloduo-clean-video_0ms9j8ff7_fa331543.mp4"
)
WORK = SEC / "video/work"
CLIPS = SEC / "video/clips"
OUT_FWD = CLIPS / "02-mic-orbit-into-soloduo.mp4"
OUT_REV = CLIPS / "02-mic-orbit-into-soloduo-REVERSE.mp4"

W, H = 1280, 720
FPS = 24


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd[:8]), "...")
    subprocess.check_call(cmd)


def probe_dur(path: Path) -> float:
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


def extract_frame(src: Path, t: float, dst: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{max(0.0, t):.3f}",
            "-i",
            str(src),
            "-map",
            "0:v:0",
            "-frames:v",
            "1",
            "-update",
            "1",
            "-q:v",
            "2",
            "-pix_fmt",
            "yuvj420p",
            str(dst),
        ]
    )


def white_border_frac(path: Path, thr: int = 210) -> tuple[float, float, float, float]:
    a = np.asarray(Image.open(path).convert("RGB"))
    h, w, _ = a.shape
    white = (a.min(axis=2) >= thr) & (a.std(axis=2) < 28)

    def edge_run(mask_1d: np.ndarray) -> int:
        n = 0
        for v in mask_1d:
            if v:
                n += 1
            else:
                break
        return n

    col_white = white.mean(axis=0) > 0.5
    row_white = white.mean(axis=1) > 0.5
    left = edge_run(col_white)
    right = edge_run(col_white[::-1])
    top = edge_run(row_white)
    bot = edge_run(row_white[::-1])
    return left / w, right / w, top / h, bot / h


def smoothstep(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"missing {SRC}")
    WORK.mkdir(parents=True, exist_ok=True)
    CLIPS.mkdir(parents=True, exist_ok=True)

    dur = probe_dur(SRC)
    last = WORK / "mic-clean-last-raw.jpg"
    extract_frame(SRC, max(0.0, dur - 0.12), last)
    l, r, t, b = white_border_frac(last)
    print(f"border fractions LRTB={l:.3f},{r:.3f},{t:.3f},{b:.3f}")

    need = max(l, r, t, b) * 2 + 0.06
    need = min(max(need, 0.10), 0.32)
    z_end = 1.0 / (1.0 - need)
    z_end = min(max(z_end, 1.12), 1.40)
    print(f"z_end={z_end:.4f}")

    # Zoom only in the last zoom_secs (when UI fills the frame)
    zoom_secs = 2.2
    t0 = max(0.0, dur - zoom_secs)
    n_frames = int(round(dur * FPS))
    i0 = int(round(t0 * FPS))

    # Build per-frame zoom list (monotonic, smoothstep ease-in)
    zooms: list[float] = []
    for i in range(n_frames):
        if i <= i0:
            zooms.append(1.0)
        else:
            u = (i - i0) / max(1, (n_frames - 1 - i0))
            zooms.append(1.0 + (z_end - 1.0) * smoothstep(u))

    # Encode with sendcmd-less approach: zoompan BUT with trunc x/y and
    # pre-rounded zoom table via a simplified expression that matches smoothstep.
    # More reliable: use Python to drive a concat of short crops — too heavy.
    # Use zoompan with:
    #   z monotonic smoothstep approx: u^2 * (3-2u) via poly
    #   x/y = trunc(...)
    on0 = i0
    denom = max(1, n_frames - 1 - on0)
    # smoothstep(u)=u*u*(3-2*u); u=(on-on0)/denom
    # z=1+(zend-1)*smoothstep
    z_expr = (
        f"if(lte(on\\,{on0})\\,1\\,"
        f"1+({z_end:.6f}-1)*("
        f"pow((on-{on0})/{denom}\\,2)*(3-2*((on-{on0})/{denom}))"
        f"))"
    )
    # CRITICAL shake fix: integer pixel pan
    x_expr = "trunc(iw/2-iw/zoom/2)"
    y_expr = "trunc(ih/2-ih/zoom/2)"

    zoomed = WORK / "mic-orbit-zoomed-end.mp4"
    # Super-sample path: scale to 2x first, zoompan at 2x, downscale — reduces shimmer
    vf = (
        f"fps={FPS},scale={W * 2}:{H * 2}:flags=lanczos,"
        f"zoompan=z='{z_expr}':x='{x_expr}':y='{y_expr}':"
        f"d=1:s={W * 2}x{H * 2}:fps={FPS},"
        f"scale={W}:{H}:flags=lanczos,format=yuv420p"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(SRC),
            "-vf",
            vf,
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "17",
            "-t",
            f"{dur:.3f}",
            "-movflags",
            "+faststart",
            str(zoomed),
        ]
    )

    last2 = WORK / "mic-zoomed-last.jpg"
    extract_frame(zoomed, max(0.0, probe_dur(zoomed) - 0.12), last2)
    borders = white_border_frac(last2)
    print("after zoom borders", borders)

    # If border remains, one more static end-crop pass (stable, no pan jitter)
    if max(borders) > 0.008:
        # measure needed crop on last frame
        l2, r2, t2, b2 = borders
        # extra zoom factor
        extra = 1.0 / (1.0 - min(0.3, max(l2, r2, t2, b2) * 2 + 0.04))
        z2 = min(z_end * extra, 1.5)
        print(f"extra static polish z={z2:.3f}")
        # apply gentle additional zoom only last 1.0s with trunc
        on1 = int(round((dur - 1.0) * FPS))
        den1 = max(1, n_frames - 1 - on1)
        z_expr2 = (
            f"if(lte(on\\,{on1})\\,1\\,"
            f"1+({z2 / z_end:.6f}-1)*("  # relative to already-zoomed
            f"pow((on-{on1})/{den1}\\,2)*(3-2*((on-{on1})/{den1}))"
            f"))"
        )
        # simpler: overall z from 1 to z2 from start of zoom window
        z_expr2 = (
            f"if(lte(on\\,{on0})\\,1\\,"
            f"1+({z2:.6f}-1)*("
            f"pow((on-{on0})/{denom}\\,2)*(3-2*((on-{on0})/{denom}))"
            f"))"
        )
        vf2 = (
            f"fps={FPS},scale={W * 2}:{H * 2}:flags=lanczos,"
            f"zoompan=z='{z_expr2}':x='{x_expr}':y='{y_expr}':"
            f"d=1:s={W * 2}x{H * 2}:fps={FPS},"
            f"scale={W}:{H}:flags=lanczos,format=yuv420p"
        )
        run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(SRC),
                "-vf",
                vf2,
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "17",
                "-t",
                f"{dur:.3f}",
                "-movflags",
                "+faststart",
                str(zoomed),
            ]
        )
        extract_frame(zoomed, max(0.0, probe_dur(zoomed) - 0.12), last2)
        print("final borders", white_border_frac(last2))

    OUT_FWD.write_bytes(zoomed.read_bytes())

    # reverse — stable (no extra zoom)
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(OUT_FWD),
            "-vf",
            "reverse,format=yuv420p",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "17",
            "-movflags",
            "+faststart",
            str(OUT_REV),
        ]
    )

    print("FWD", OUT_FWD, probe_dur(OUT_FWD))
    print("REV", OUT_REV, probe_dur(OUT_REV))
    print("last", last2)
    # keep zooms list referenced so linters don't complain if unused later
    _ = zooms[0]


if __name__ == "__main__":
    main()
