#!/usr/bin/env python3
"""
Notch the repeating rising hum on v1 bed.
User-measured: lowest ~4.696s, highest ~8.645s, then repeats.
First 2.0s left exact.
"""

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

# User anchors
T_LOW = 4.696
T_HIGH = 8.645
PERIOD = T_HIGH - T_LOW  # ~3.949s rise; treat as full cycle low→high→(reset)
PROTECT = 2.0

# Rising hum band (Hz) across the cycle
F_AT_LOW = 140.0
F_AT_HIGH = 1400.0
NOTCH_Q = 2.8  # wider = catches more of the hum
NOTCH_DEPTH = 0.82  # 0..1 how much to remove at center (0.82 = strong)


class BiquadNotch:
    """RBJ notch, coeffs updatable each sample (slowly)."""

    def __init__(self):
        self.x1 = self.x2 = 0.0
        self.y1 = self.y2 = 0.0
        self.b0 = 1.0
        self.b1 = 0.0
        self.b2 = 0.0
        self.a1 = 0.0
        self.a2 = 0.0

    def set(self, sr: int, f0: float, q: float) -> None:
        f0 = max(40.0, min(f0, sr * 0.45))
        w0 = 2 * math.pi * f0 / sr
        alpha = math.sin(w0) / (2 * q)
        cosw = math.cos(w0)
        b0 = 1.0
        b1 = -2 * cosw
        b2 = 1.0
        a0 = 1 + alpha
        a1 = -2 * cosw
        a2 = 1 - alpha
        self.b0 = b0 / a0
        self.b1 = b1 / a0
        self.b2 = b2 / a0
        self.a1 = a1 / a0
        self.a2 = a2 / a0

    def process(self, x: float) -> float:
        y = self.b0 * x + self.b1 * self.x1 + self.b2 * self.x2 - self.a1 * self.y1 - self.a2 * self.y2
        self.x2, self.x1 = self.x1, x
        self.y2, self.y1 = self.y1, y
        return y


def hum_freq(t: str | float) -> float:
    """Center frequency of rising hum at time t (seconds)."""
    # phase 0 at T_LOW (lowest), phase 1 at T_HIGH (highest), then wrap
    # Use period = PERIOD for rise; after high, snap back (or fall quickly)
    ph = (float(t) - T_LOW) / PERIOD
    # wrap to 0..1
    ph = ph - math.floor(ph)
    # smooth rise 0→1, quick return in last 8% so it "repeats"
    if ph < 0.92:
        u = ph / 0.92
        u = u * u * (3 - 2 * u)  # smoothstep rise
    else:
        u = 1.0 - (ph - 0.92) / 0.08  # quick fall
        u = max(0.0, u)
    return F_AT_LOW + (F_AT_HIGH - F_AT_LOW) * u


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

    x = [s / 32768.0 for s in samp]
    protect = int(PROTECT * sr)

    # cascade two notches for deeper cut on the sweep
    n1, n2 = BiquadNotch(), BiquadNotch()
    # mild shelf LPF after protect to settle residual zing
    lpf_y = 0.0
    lpf_a = math.exp(-2 * math.pi * 6500 / sr)

    out = array("h")
    # exact first 2s
    for i in range(protect):
        out.append(int(max(-1, min(1, x[i])) * 32767))

    # prime filters with protected audio (no write change)
    for i in range(protect):
        t = i / sr
        f0 = hum_freq(t)
        n1.set(sr, f0, NOTCH_Q)
        n2.set(sr, f0 * 1.12, NOTCH_Q * 0.9)  # slight spread
        y = n1.process(x[i])
        y = n2.process(y)
        lpf_y = (1 - lpf_a) * y + lpf_a * lpf_y

    for i in range(protect, n):
        t = i / sr
        f0 = hum_freq(t)
        # update coeffs every ~64 samples (smooth enough, cheaper)
        if (i - protect) % 64 == 0:
            n1.set(sr, f0, NOTCH_Q)
            n2.set(sr, f0 * 1.15, NOTCH_Q * 0.85)

        dry = x[i]
        wet = n2.process(n1.process(dry))
        # blend notch amount
        y = dry * (1.0 - NOTCH_DEPTH) + wet * NOTCH_DEPTH

        # light LPF
        lpf_y = (1 - lpf_a) * y + lpf_a * lpf_y
        y = y * 0.75 + lpf_y * 0.25

        # soft edge in
        edge = min(1.0, (i - protect) / (0.08 * sr))
        y = dry * (1 - edge) + y * edge
        y = math.tanh(y * 1.03)
        out.append(int(max(-1, min(1, y)) * 32767))

    # match loudness after protect to v1
    peak = 1e-9
    p1 = 1e-9
    for i in range(protect, n):
        peak = max(peak, abs(out[i] / 32768.0))
        p1 = max(p1, abs(x[i]))
    g = min(1.2, (p1 * 0.96) / peak)
    for i in range(protect, n):
        z = out[i] / 32768.0 * g
        out[i] = int(max(-1, min(1, z)) * 32767)

    with wave.open(str(OUT_WAV), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(out.tobytes())

    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(OUT_WAV), "-c:a", "libmp3lame", "-b:a", "192k", str(OUT_MP3)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    V1_WAV.unlink(missing_ok=True)
    print(
        f"notched rising hum period={PERIOD:.3f}s "
        f"f={F_AT_LOW:.0f}->{F_AT_HIGH:.0f}Hz anchors {T_LOW}-{T_HIGH}s"
    )
    print(OUT_MP3)


if __name__ == "__main__":
    main()
