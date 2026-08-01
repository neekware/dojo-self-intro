#!/usr/bin/env python3
"""17.00.00-credits: slow zoom on LOCKED still + Eve giants VO.

Picture: gentle Ken Burns (1.0 → ~1.12), centered on the name field.
Audio: Eve VO with lead-in / tail pad. Duration measured from VO file.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/17.00.00-credits"
STILL = SEC / "after/final/credits-LOCKED-1920.jpg"
VO_SRC = SEC / "audio/final/credits-giants-vo.mp3"
WORK = SEC / "video/work"
AUDIO_WORK = SEC / "audio/work"
OUT = SEC / "video/final/LOCKED-16-credits.mp4"
# keep old name as alias copy for earlier refs
OUT_ALIAS = SEC / "video/final/LOCKED-16-credits-hold.mp4"

PAD_IN = 0.70  # breath before VO
PAD_OUT = 1.30  # hold after last word
ZOOM_END = 1.12  # slow push-in (not aggressive)
FPS = 30


def probe_duration(path: Path) -> float:
    out = subprocess.check_output(
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
    return float(out)


def main() -> None:
    if not STILL.exists():
        raise SystemExit(f"missing still: {STILL}")
    if not VO_SRC.exists():
        raise SystemExit(f"missing VO: {VO_SRC}")

    WORK.mkdir(parents=True, exist_ok=True)
    AUDIO_WORK.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    vo_dur = probe_duration(VO_SRC)
    total = PAD_IN + vo_dur + PAD_OUT
    n_frames = int(round(total * FPS))
    # zoompan z expression: 1.0 → ZOOM_END over n_frames
    # on = output frame number starting at 0
    z_expr = f"1+{(ZOOM_END - 1.0):.6f}*on/{max(n_frames - 1, 1)}"

    # Pad VO: silence lead + VO + silence tail, stereo 48k
    padded_vo = AUDIO_WORK / "credits-giants-vo-padded.m4a"
    # adelay is ms; apad for tail
    delay_ms = int(round(PAD_IN * 1000))
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(VO_SRC),
            "-af",
            f"aformat=sample_rates=48000:channel_layouts=stereo,"
            f"adelay={delay_ms}|{delay_ms},"
            f"apad=pad_dur={PAD_OUT}",
            "-t",
            f"{total:.3f}",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(padded_vo),
        ]
    )

    # Slow zoom video + mux padded VO
    # Upscale still first so zoompan has pixels to crop into
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(STILL),
            "-i",
            str(padded_vo),
            "-filter_complex",
            (
                f"[0:v]scale=8000:-1,"
                f"zoompan=z='{z_expr}':"
                f"x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':"
                f"d=1:s=1920x1080:fps={FPS},"
                f"format=yuv420p[v]"
            ),
            "-map",
            "[v]",
            "-map",
            "1:a",
            "-t",
            f"{total:.3f}",
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
            "-ar",
            "48000",
            "-ac",
            "2",
            "-shortest",
            "-movflags",
            "+faststart",
            str(OUT),
        ]
    )

    shutil.copy2(OUT, OUT_ALIAS)

    probe = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration,size",
            "-show_entries",
            "stream=codec_name,width,height,r_frame_rate,codec_type",
            "-of",
            "default=noprint_wrappers=1",
            str(OUT),
        ],
        text=True,
    )
    print(f"VO_DUR={vo_dur:.3f}s  PAD_IN={PAD_IN}  PAD_OUT={PAD_OUT}  TOTAL={total:.3f}s")
    print(f"FRAMES={n_frames}  ZOOM 1.00→{ZOOM_END}")
    print(probe)
    print("OUT", OUT, OUT.stat().st_size)


if __name__ == "__main__":
    main()
