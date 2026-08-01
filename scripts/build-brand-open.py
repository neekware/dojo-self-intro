#!/usr/bin/env python3
"""Brand open: gem/neural hero hold → soft morph into startup open (lion/welcome).

Torii splash stills remain on disk (splash-LOCKED*) but are NOT used in the open —
gem hero is the eye-catching open + reel thumb.
Giants / credits are NOT in brand open — they open What is Dojo (01.00.00).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/00.00.00-brand"
# Active open still (gem / neural hero). Torii splash kept unused.
OPEN_STILL = SEC / "after/final/brand-open-still-LOCKED-1920x1080.jpg"
OPEN_STILL_PNG = SEC / "after/final/brand-open-still-LOCKED.png"
# Unused (kept): splash-LOCKED-1920x1080.jpg, splash-LOCKED.png
STARTUP = SEC / "video/startup/LOCKED-00-startup-open.mp4"
OUT = SEC / "video/final/LOCKED-00-brand-open.mp4"
TMP = SEC / "video/startup/_tmp"
HOLD_SEC = 2.0
# Soft morph open still → lion
XFADE = 1.2


def normalize(src: Path, dst: Path, has_audio: bool) -> None:
    if has_audio:
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(src),
                "-vf",
                "fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,"
                "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,format=yuv420p",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
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
                str(dst),
            ]
        )
    else:
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(src),
                "-f",
                "lavfi",
                "-i",
                "anullsrc=channel_layout=stereo:sample_rate=48000",
                "-vf",
                "fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,"
                "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,format=yuv420p",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "18",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-shortest",
                "-movflags",
                "+faststart",
                str(dst),
            ]
        )


def duration(path: Path) -> float:
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


def main() -> None:
    if not STARTUP.exists():
        raise SystemExit(f"missing startup: {STARTUP}")

    TMP.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    open_still = OPEN_STILL if OPEN_STILL.exists() else OPEN_STILL_PNG
    if not open_still.exists():
        raise SystemExit(f"missing open still: {OPEN_STILL}")

    open_1080 = TMP / "open-still-1920.jpg"
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(open_still),
            "-frames:v",
            "1",
            "-update",
            "1",
            "-vf",
            "scale=1920:1080:force_original_aspect_ratio=decrease,"
            "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black",
            "-q:v",
            "2",
            str(open_1080),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    open_mp4 = TMP / "open-hold.mp4"
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(open_1080),
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-t",
            str(HOLD_SEC),
            "-r",
            "30",
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
            "-shortest",
            "-movflags",
            "+faststart",
            str(open_mp4),
        ]
    )

    startup_n = TMP / "startup-n.mp4"
    normalize(STARTUP, startup_n, has_audio=True)

    d0 = duration(open_mp4)
    d1 = duration(startup_n)
    o1 = d0 - XFADE
    expected = d0 + d1 - XFADE

    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(open_mp4),
            "-i",
            str(startup_n),
            "-filter_complex",
            (
                f"[0:v][1:v]xfade=transition=fade:duration={XFADE}:offset={o1:.3f}[v];"
                f"[0:a][1:a]acrossfade=d={XFADE}:c1=tri:c2=tri[a]"
            ),
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
            "-movflags",
            "+faststart",
            str(OUT),
        ]
    )

    print(f"open_still={d0:.3f}s startup={d1:.3f}s xfade={XFADE} expected≈{expected:.3f}s")
    print("still", open_still)
    print("OUT", OUT, OUT.stat().st_size, "dur", duration(OUT))


if __name__ == "__main__":
    main()
