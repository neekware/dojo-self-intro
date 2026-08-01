#!/usr/bin/env python3
"""17 connection picture: forward → reverse → forward (smooth smile / no hard seam).

Drops the duplicated endpoint frame at each turnaround so motion doesn't freeze 1 frame.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/01.00.00-what-is-dojo"
FINAL = SEC / "video/final"
WORK = SEC / "video/work"
PIC = FINAL / "LOCKED-01-connection.mp4"
SRC = WORK / "LOCKED-01-connection-forward-only-SOURCE.mp4"
OUT_WORK = WORK / "LOCKED-01-connection-pingpong.mp4"


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd[:8]), "...")
    subprocess.check_call(cmd)


def probe(path: Path) -> str:
    return subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-show_entries",
            "stream=nb_frames,width,height",
            "-of",
            "default=noprint_wrappers=1",
            str(path),
        ],
        text=True,
    )


def frame_count(path: Path) -> int:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-count_frames",
            "-show_entries",
            "stream=nb_read_frames",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        text=True,
    ).strip()
    return int(out)


def main() -> None:
    WORK.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)

    if not SRC.exists():
        if not PIC.exists():
            raise SystemExit(f"missing picture: {PIC}")
        SRC.write_bytes(PIC.read_bytes())
        print("archived forward-only source →", SRC)

    n = frame_count(SRC)
    # forward: all frames 0..n-1
    # reverse without first (was last of forward): frames n-2 .. 0  → n-1 frames
    # forward without first (was last of reverse = frame 0): frames 1..n-1 → n-1 frames
    # filter: [0:v]split=3[f][r][f2];
    #   [f] setpts
    #   [r] reverse, trim=start_frame=1
    #   [f2] trim=start_frame=1
    # concat
    fc = (
        "[0:v]split=3[f0][r0][f1];"
        "[f0]setpts=PTS-STARTPTS[fwd1];"
        f"[r0]reverse,trim=start_frame=1,setpts=PTS-STARTPTS[rev];"
        f"[f1]trim=start_frame=1,setpts=PTS-STARTPTS[fwd2];"
        "[fwd1][rev][fwd2]concat=n=3:v=1:a=0[v]"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(SRC),
            "-filter_complex",
            fc,
            "-map",
            "[v]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(OUT_WORK),
        ]
    )

    PIC.write_bytes(OUT_WORK.read_bytes())
    print("source_frames", n)
    print("installed", PIC)
    print(probe(PIC))
    # expected ~ n + (n-1) + (n-1) = 3n - 2
    print("expected_frames", 3 * n - 2)


if __name__ == "__main__":
    main()
