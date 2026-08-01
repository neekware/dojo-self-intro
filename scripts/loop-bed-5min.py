#!/usr/bin/env python3
"""Smooth-loop locked bed to ~5 minutes."""

from __future__ import annotations

import math
import subprocess
import wave
from array import array
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "public/sections/00.00.00-brand/audio"
FINAL = BASE / "final"
SRC_MP3 = FINAL / "bg-bed-locked.mp3"
SRC_WAV = FINAL / "_bed_src.wav"
OUT_WAV = FINAL / "bg-bed-locked-5min.wav"
OUT_MP3 = FINAL / "bg-bed-locked-5min.mp3"
LONG_ALIAS = FINAL / "bg-bed-locked-LONG.mp3"
ROOT_LONG = BASE / "BACKGROUND-BED-LOCKED-5min-12pct.mp3"

TARGET = 5 * 60.0
XFADE = 2.0


def main() -> None:
    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(SRC_MP3), "-ac", "1", "-ar", "44100", str(SRC_WAV)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    with wave.open(str(SRC_WAV), "rb") as w:
        sr = w.getframerate()
        n = w.getnframes()
        samp = array("h")
        samp.frombytes(w.readframes(n))

    x = [s / 32768.0 for s in samp]
    xf = int(XFADE * sr)
    body = n - xf
    k = max(0, math.ceil((TARGET * sr - n) / body))
    total_n = n + k * body

    out = [0.0] * total_n
    for i in range(n):
        out[i] = x[i]

    pos = n
    for _ in range(k):
        start = pos - xf
        for i in range(xf):
            t = i / max(1, xf - 1)
            a = math.cos(t * math.pi / 2)
            b = math.sin(t * math.pi / 2)
            out[start + i] = out[start + i] * a + x[i] * b
        for i in range(xf, n):
            out[pos + (i - xf)] = x[i]
        pos += body

    target_n = int(TARGET * sr)
    if len(out) > target_n:
        out = out[:target_n]
    elif len(out) < target_n:
        out.extend([0.0] * (target_n - len(out)))

    end_fade = int(1.5 * sr)
    for i in range(end_fade):
        out[target_n - 1 - i] *= i / end_fade

    peak = max(1e-9, max(abs(v) for v in out))
    g = 0.92 / peak
    pcm = array("h")
    for v in out:
        y = max(-1.0, min(1.0, v * g))
        pcm.append(int(y * 32767))

    with wave.open(str(OUT_WAV), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())

    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(OUT_WAV), "-c:a", "libmp3lame", "-b:a", "192k", str(OUT_MP3)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.check_call(["cp", "-f", str(OUT_MP3), str(LONG_ALIAS)])
    subprocess.check_call(["cp", "-f", str(OUT_MP3), str(ROOT_LONG)])
    SRC_WAV.unlink(missing_ok=True)
    print(f"wrote {OUT_MP3} duration={target_n/sr:.2f}s loops_after_first={k} xfade={XFADE}s")


if __name__ == "__main__":
    main()
