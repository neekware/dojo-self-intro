#!/usr/bin/env python3
"""Reduce low→high rising hum on v1 bed; keep first 2s exact."""

from __future__ import annotations

import math
import subprocess
import wave
from array import array
from pathlib import Path

AUDIO = Path(__file__).resolve().parents[1] / "public/sections/00.00.00-brand/audio"
V1_MP3 = AUDIO / "dojo-bed-instrumental-v1-harsh.mp3"
V1_WAV = AUDIO / "_v1.wav"
OUT_WAV = AUDIO / "dojo-bed-instrumental.wav"
OUT_MP3 = AUDIO / "dojo-bed-instrumental.mp3"


class LPF:
    def __init__(self, fc: float, sr: int):
        self.y = 0.0
        self.a = math.exp(-2 * math.pi * fc / sr)

    def __call__(self, v: float) -> float:
        self.y = (1 - self.a) * v + self.a * self.y
        return self.y


def main() -> None:
    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(V1_MP3), "-ac", "1", "-ar", "44100", str(V1_WAV)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    with wave.open(str(V1_WAV), "rb") as w:
        sr = w.getframerate()
        n = w.getnframes()
        samp = array("h")
        samp.frombytes(w.readframes(n))

    v1 = [s / 32768.0 for s in samp]
    protect = int(2.0 * sr)

    lp_body = LPF(280, sr)
    lp_hum = LPF(950, sr)
    lp_top = LPF(3200, sr)
    lp_out = LPF(4200, sr)

    out: list[float] = []
    for i in range(protect):
        out.append(v1[i])

    # prime filters
    for i in range(protect):
        v = v1[i]
        lp_body(v)
        lp_hum(v)
        lp_top(v)

    prev_ratio = 0.0
    for i in range(protect, n):
        v = v1[i]
        body = lp_body(v)
        hum_full = lp_hum(v)
        top_full = lp_top(v)
        hum = hum_full - body
        upper = top_full - hum_full
        air = v - top_full

        e_hum = abs(hum)
        e_up = abs(upper)
        ratio = e_up / (e_hum + 1e-4)
        prev_ratio = prev_ratio * 0.995 + ratio * 0.005

        up_gain = 0.38
        if prev_ratio > 0.85:
            up_gain *= 0.5
        elif prev_ratio > 0.55:
            up_gain *= 0.68

        y = body * 1.06 + hum * 0.75 + upper * up_gain + air * 0.30
        out.append(y)

    final = array("h")
    for i, y in enumerate(out):
        if i < protect:
            final.append(int(max(-1.0, min(1.0, y)) * 32767))
        else:
            edge = min(1.0, (i - protect) / (0.1 * sr))
            f = lp_out(y)
            z = y * (1 - 0.3 * edge) + f * (0.3 * edge)
            z = math.tanh(z * 1.04)
            final.append(int(max(-1.0, min(1.0, z)) * 32767))

    peak = 1e-9
    p1 = 1e-9
    for i in range(protect, n):
        peak = max(peak, abs(final[i] / 32768.0))
        p1 = max(p1, abs(v1[i]))
    g = min(1.15, (p1 * 0.95) / peak)
    for i in range(protect, n):
        z = final[i] / 32768.0 * g
        final[i] = int(max(-1.0, min(1.0, z)) * 32767)

    with wave.open(str(OUT_WAV), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(final.tobytes())

    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(OUT_WAV), "-c:a", "libmp3lame", "-b:a", "192k", str(OUT_MP3)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    V1_WAV.unlink(missing_ok=True)
    print("done", OUT_MP3)


if __name__ == "__main__":
    main()
