#!/usr/bin/env python3
"""Stitch: orbit-into-IDE (end-zoom no bezel) → mic reverse (zoom out to voice)."""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/02.00.00-stt-talk"
WORK = SEC / "video/work"
CLIPS = SEC / "video/clips"

IDE_SRC = (
    Path.home()
    / ".dojo/workspace/artifacts/ads-b9196c98/video-gen"
    / "code-orbit-into-ide-flat-video_0ms9iyhgc_df72becb.mp4"
)
MIC_REV = CLIPS / "02-mic-orbit-into-soloduo-REVERSE.mp4"
OUT = CLIPS / "03-ide-in-mic-out.mp4"

W, H, FPS = 1280, 720, 24
XFADE = 0.45  # short soft join at full-UI


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd[:10]), "...")
    subprocess.check_call(cmd)


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


def extract(src: Path, t: float, dst: Path) -> None:
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


def edge_dark_or_bright_frac(path: Path) -> float:
    """How much non-UI edge (bright bezel OR very dark frame) on borders."""
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.float32)
    h, w, _ = a.shape
    mean = a.mean(axis=2)
    # bezel-ish: bright gray/white OR solid black frame
    bright = mean >= 200
    # sample 3% edge strips
    ew, eh = max(2, w // 30), max(2, h // 30)
    left = bright[:, :ew].mean()
    right = bright[:, -ew:].mean()
    top = bright[:eh, :].mean()
    bot = bright[-eh:, :].mean()
    return float(max(left, right, top, bot))


def smooth_end_zoom(src: Path, dst: Path, z_end: float, zoom_secs: float = 2.0) -> None:
    dur = probe(src)
    n = int(round(dur * FPS))
    on0 = int(round(max(0.0, dur - zoom_secs) * FPS))
    denom = max(1, n - 1 - on0)
    z_expr = (
        f"if(lte(on\\,{on0})\\,1\\,"
        f"1+({z_end:.6f}-1)*("
        f"pow((on-{on0})/{denom}\\,2)*(3-2*((on-{on0})/{denom}))"
        f"))"
    )
    x_expr = "trunc(iw/2-iw/zoom/2)"
    y_expr = "trunc(ih/2-ih/zoom/2)"
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
            str(src),
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
            str(dst),
        ]
    )


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    CLIPS.mkdir(parents=True, exist_ok=True)
    if not IDE_SRC.exists():
        raise SystemExit(f"missing {IDE_SRC}")
    if not MIC_REV.exists():
        raise SystemExit(f"missing {MIC_REV}")

    # 1) end-zoom IDE clip until bezel gone
    last0 = WORK / "ide-last-raw.jpg"
    extract(IDE_SRC, probe(IDE_SRC) - 0.12, last0)
    edge = edge_dark_or_bright_frac(last0)
    print("ide last edge bright frac", edge)
    # bezel usually needs ~1.15–1.28 zoom
    z = 1.18 if edge < 0.08 else min(1.35, 1.12 + edge)
    print("using z_end", z)
    ide_z = WORK / "ide-orbit-zoomed-end.mp4"
    smooth_end_zoom(IDE_SRC, ide_z, z_end=z, zoom_secs=2.2)

    last1 = WORK / "ide-last-zoomed.jpg"
    extract(ide_z, probe(ide_z) - 0.12, last1)
    print("after zoom edge", edge_dark_or_bright_frac(last1))
    # second bump if needed
    if edge_dark_or_bright_frac(last1) > 0.04:
        z2 = min(z * 1.12, 1.4)
        print("second zoom", z2)
        smooth_end_zoom(IDE_SRC, ide_z, z_end=z2, zoom_secs=2.2)
        extract(ide_z, probe(ide_z) - 0.12, last1)
        print("final edge", edge_dark_or_bright_frac(last1))

    # 2) normalize mic reverse
    mic_n = WORK / "mic-rev-n.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(MIC_REV),
            "-vf",
            f"fps={FPS},scale={W}:{H}:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,format=yuv420p,setsar=1",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "17",
            "-movflags",
            "+faststart",
            str(mic_n),
        ]
    )

    d0 = probe(ide_z)
    d1 = probe(mic_n)
    if d0 <= XFADE + 0.05 or d1 <= XFADE + 0.05:
        raise SystemExit("clips too short for xfade")
    off = d0 - XFADE
    expected = d0 + d1 - XFADE

    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(ide_z),
            "-i",
            str(mic_n),
            "-filter_complex",
            (
                f"[0:v]fps={FPS},format=yuv420p,setpts=PTS-STARTPTS[v0];"
                f"[1:v]fps={FPS},format=yuv420p,setpts=PTS-STARTPTS[v1];"
                f"[v0][v1]xfade=transition=fade:duration={XFADE:.3f}:offset={off:.3f},format=yuv420p[v]"
            ),
            "-map",
            "[v]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "17",
            "-t",
            f"{expected:.3f}",
            "-movflags",
            "+faststart",
            str(OUT),
        ]
    )

    # also keep zoomed ide alone for reuse
    (CLIPS / "01-orbit-into-ide.mp4").write_bytes(ide_z.read_bytes())

    print(f"ide={d0:.3f}s mic_rev={d1:.3f}s xfade={XFADE} OUT={probe(OUT):.3f}s")
    print(OUT, OUT.stat().st_size)
    print("last frames:", last1)


if __name__ == "__main__":
    main()
