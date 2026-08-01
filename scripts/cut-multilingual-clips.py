#!/usr/bin/env python3
"""Detect VO onset in each language clip and cut it with consistent headroom.

Each source clip is the same 7.04s picture with a short VO centered in it.
We measure where the voice actually starts/ends, then cut with a fixed lead-in
and tail so every language gets identical breathing room.
"""
from __future__ import annotations

import io
import math
import struct
import subprocess
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEC = ROOT / "public/sections/13.00.00-multilingual"
CLIPS = SEC / "video/clips"
CUTS = SEC / "video/cuts"

LEAD_IN = 0.150    # silence kept before the first phoneme
TAIL_OUT = 0.280   # silence kept after the last phoneme
THRESH_PCT = 0.06  # onset threshold as fraction of peak RMS

ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart"]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def dur(p: Path) -> float:
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)], text=True).strip())


def onset_window(clip: Path) -> tuple[float, float]:
    """Return (start, end) seconds of actual speech in the clip."""
    wav = subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", str(clip), "-map", "0:a", "-f", "wav", "-"],
        stderr=subprocess.DEVNULL)
    w = wave.open(io.BytesIO(wav), "rb")
    sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
    frames = w.readframes(n)
    step = int(sr * 0.02)

    vals: list[tuple[float, float]] = []
    for s in range(0, n, step):
        chunk = frames[s * ch * 2:(s + step) * ch * 2]
        if not chunk:
            break
        samples = struct.unpack(f"{len(chunk) // 2}h", chunk)
        rms = math.sqrt(sum(x * x for x in samples) / max(1, len(samples)))
        vals.append((s / sr, rms))

    peak = max(v for _, v in vals)
    thr = peak * THRESH_PCT
    start = next((t for t, v in vals if v > thr), 0.0)
    end = next((t for t, v in reversed(vals) if v > thr), dur(clip))
    return start, end


def main() -> None:
    CUTS.mkdir(parents=True, exist_ok=True)
    langs = ["en", "zh", "fa", "fr", "ar", "ja", "es"]

    for lang in langs:
        src = CLIPS / f"clip-{lang}.mp4"
        if not src.exists():
            print(f"skip {lang}: missing {src.name}")
            continue

        start, end = onset_window(src)
        clip_len = dur(src)
        cut_in = max(0.0, start - LEAD_IN)
        cut_out = min(clip_len, end + TAIL_OUT)

        out = CUTS / f"cut-{lang}.mp4"
        run(["ffmpeg", "-y", "-i", str(src), "-ss", f"{cut_in:.3f}", "-to", f"{cut_out:.3f}",
             *ENC, str(out)])

        print(f"{lang.upper():>3}  voice {start:5.3f}-{end:5.3f}  "
              f"cut {cut_in:5.3f}-{cut_out:5.3f}  -> {dur(out):5.3f}s")


if __name__ == "__main__":
    main()
