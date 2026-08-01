#!/usr/bin/env python3
"""
dee dee dee dee / doo doo doo  (repeat)
+ warm Hummmmm
+ drum DROP
Simple, catchy, no rising-hum crap.
"""

from __future__ import annotations

import math
import subprocess
import wave
from array import array
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "public/sections/00.00.00-brand/audio"
WAV = OUT / "dojo-bed-drums-drop.wav"
MP3 = OUT / "dojo-bed-drums-drop.mp3"

SR = 44100
BPM = 92  # same pocket as first bed they liked
BEAT = 60.0 / BPM
DUR = 48.0
N = int(SR * DUR)


def clamp(x, a=-1.0, b=1.0):
    return a if x < a else b if x > b else x


def sine(f, t, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def noise(i):
    x = math.sin(i * 12.9898 + 78.233) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


class LPF:
    def __init__(self, fc):
        self.y = 0.0
        self.set(fc)

    def set(self, fc):
        self.a = math.exp(-2 * math.pi * clamp(fc, 20, SR * 0.42) / SR)

    def __call__(self, x):
        self.y = (1 - self.a) * x + self.a * self.y
        return self.y


def pluck(buf, t0, freq, amp, dur=0.28, bright=0.0):
    """Soft fixed-pitch pluck — no pitch glide."""
    n = int(dur * SR)
    i0 = int(t0 * SR)
    lp = LPF(1800)
    for k in range(n):
        i = i0 + k
        if i < 0 or i >= N:
            continue
        t = k / SR
        # attack
        if t < 0.008:
            e = t / 0.008
        else:
            e = math.exp(-(t - 0.008) * 9)
        # mostly fundamental (the "dee/doo" they can hum)
        s = sine(freq, t0 + t) * 0.85 + sine(freq * 2, t0 + t) * (0.08 + 0.1 * bright)
        buf[i] += lp(s) * e * amp


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # archive last attempt
    bad = OUT / "dojo-bed-drums-drop-v2.mp3"
    if MP3.exists():
        try:
            if not bad.exists():
                MP3.replace(bad)
        except Exception:
            pass

    buf = array("f", [0.0] * N)
    lp_hum = LPF(420)  # warm hum — FIXED pitch, no sweep
    lp_hat = LPF(5000)
    lp_bass = LPF(130)
    lp_master = LPF(7000)

    # --- Melody they asked for ---
    # dee dee dee dee  (higher)  then  doo doo doo (lower)
    # note length = 1/2 beat; pattern length = 7 eighths + rest = 4 beats (1 bar)
    DEE = 329.63  # E4
    DOO = 220.00  # A3
    # pattern in eighth-notes: D D D D - O O O
    pattern = [
        (0.0, DEE, 0.9),
        (0.5, DEE, 0.85),
        (1.0, DEE, 0.85),
        (1.5, DEE, 0.95),
        # small gap
        (2.5, DOO, 1.0),
        (3.0, DOO, 0.95),
        (3.5, DOO, 1.05),
    ]

    for bar in range(int(DUR / (4 * BEAT)) + 1):
        base = bar * 4 * BEAT
        # arrangement: always the hook (that's the part they wanted)
        if base < 2.0:
            # first 2s gentler (like first bed opening)
            amp_m = 0.11
        elif base < 16:
            amp_m = 0.14
        elif base < 20:
            amp_m = 0.12  # make room for hum swell into drop
        elif base < 36:
            amp_m = 0.16  # on top of drop
        else:
            amp_m = 0.11

        for eighth, freq, rel in pattern:
            t0 = base + eighth * BEAT
            if t0 >= DUR - 0.3:
                continue
            pluck(buf, t0, freq, amp_m * rel, dur=0.32 if freq == DOO else 0.26, bright=0.15)

    # --- Hummmmm (steady low drone — NOT rising) ---
    # enters ~ after a few bars, holds, louder into drop
    HUM_F = 110.0  # A2 steady
    for i in range(N):
        t = i / SR
        # fade in from 4s, strong 12-20, big under drop, soft out
        if t < 4:
            hg = 0.0
        elif t < 8:
            hg = (t - 4) / 4 * 0.35
        elif t < 16:
            hg = 0.4
        elif t < 20:
            hg = 0.4 + 0.35 * ((t - 16) / 4)  # swell level only, pitch fixed
        elif t < 36:
            hg = 0.7
        else:
            hg = 0.7 * max(0.0, 1.0 - (t - 36) / 10)

        # gentle amplitude vibrato only (not pitch)
        vib = 1.0 + 0.03 * sine(0.8, t)
        h = sine(HUM_F, t) * 0.7 + sine(HUM_F * 2, t) * 0.12 + sine(HUM_F * 3, t) * 0.04
        buf[i] += lp_hum(h) * hg * 0.28 * vib

    # soft pad bed under everything (dark)
    pad_ch = [
        [130.81, 164.81, 196.0],
        [174.61, 220.0, 261.63],
        [98.0, 130.81, 196.0],
        [146.83, 174.61, 220.0],
    ]
    lp_pad = LPF(800)
    csec = 8 * BEAT
    for i in range(N):
        t = i / SR
        ci = int(t / csec) % 4
        s = 0.0
        for j, f in enumerate(pad_ch[ci]):
            s += 0.12 * sine(f, t, j * 0.5)
        g = 0.35 if t < 20 else 0.25
        buf[i] += lp_pad(s) * g * 0.22

    # --- bass ---
    roots = [55.0, 43.65, 49.0, 36.71]
    for i in range(N):
        t = i / SR
        if t < 8:
            continue
        ci = int(t / csec) % 4
        f = roots[ci]
        local = t % BEAT
        e = 0.4 + 0.6 * (1.0 if local < 0.4 else max(0.3, 1 - (local - 0.4) / 0.3))
        duck = 0.55 + 0.45 * min(1.0, local * 6) if local < 0.15 else 1.0
        b = sine(f, t) * 0.9 + sine(f * 2, t) * 0.06
        g = 0.7 if t < 20 else 1.0
        if t >= 36:
            g = 0.65
        buf[i] += lp_bass(b) * e * duck * 0.32 * g

    # --- DRUMS: light until drop, then full ---
    # kick
    for bi in range(int(DUR / BEAT) + 2):
        start = bi * BEAT
        # before drop: only 1 each 2 beats; drop: 4-floor
        if start < 12:
            if bi % 4 != 0:
                continue
            amp = 0.22
        elif start < 20:
            if bi % 2 != 0:
                continue
            amp = 0.32
        elif start < 38:
            amp = 0.48
        else:
            if bi % 2 != 0:
                continue
            amp = 0.3

        for k in range(int(0.2 * SR)):
            idx = int(start * SR) + k
            if idx >= N:
                break
            tt = k / SR
            f = 62 * math.exp(-tt * 13) + 35
            body = math.sin(2 * math.pi * f * tt) * math.exp(-tt * 10)
            buf[idx] += body * amp

    # snare 2&4 from bar 3, hard on drop
    for bi in range(int(DUR / BEAT) + 2):
        if bi % 4 not in (1, 3):
            continue
        start = bi * BEAT
        if start < 8:
            continue
        amp = 0.1 if start < 20 else 0.2
        for k in range(int(0.11 * SR)):
            idx = int(start * SR) + k
            if idx >= N:
                break
            tt = k / SR
            nse = lp_hat(noise(idx + 17)) * math.exp(-tt * 26)
            tone = sine(165, tt) * math.exp(-tt * 20) * 0.3
            buf[idx] += (nse * 0.6 + tone) * amp

    # hats
    for bi in range(int(DUR / (BEAT / 2)) + 2):
        start = bi * (BEAT / 2)
        if start < 6:
            continue
        amp = 0.018 if bi % 2 == 0 else 0.01
        if 20 <= start < 38:
            amp *= 1.35
        for k in range(int(0.02 * SR)):
            idx = int(start * SR) + k
            if idx >= N:
                break
            tt = k / SR
            h = lp_hat(noise(idx + 3)) * math.exp(-tt * 95)
            buf[idx] += h * amp

    # snare roll into drop
    for r in range(16):
        start = 19.0 + r * (0.055)
        if start >= 20:
            break
        for k in range(int(0.04 * SR)):
            idx = int(start * SR) + k
            if idx >= N:
                break
            tt = k / SR
            nse = lp_hat(noise(idx + 50 + r)) * math.exp(-tt * 45)
            buf[idx] += nse * (0.03 + 0.008 * r)

    # DROP impact + hum punch
    for k in range(int(0.55 * SR)):
        idx = int(20 * SR) + k
        if idx >= N:
            break
        tt = k / SR
        boom = sine(50 * math.exp(-tt * 2.2), tt) * math.exp(-tt * 3.2)
        # steady hum layer boost (still fixed pitch)
        hum_boost = sine(110, 20 + tt) * math.exp(-tt * 2.5) * 0.35
        buf[idx] += boom * 0.6 + hum_boost * 0.4

    # fades
    for i in range(int(0.35 * SR)):
        buf[i] *= (i / (0.35 * SR)) ** 1.2
    for i in range(int(1.4 * SR)):
        buf[N - 1 - i] *= (i / (1.4 * SR)) ** 1.1

    peak = max(1e-9, max(abs(v) for v in buf))
    g = 0.87 / peak
    out = array("h")
    for v in buf:
        y = lp_master(v * g)
        y = math.tanh(y * 1.08)
        out.append(int(clamp(y) * 32767))

    with wave.open(str(WAV), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(out.tobytes())

    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(WAV), "-c:a", "libmp3lame", "-b:a", "192k", str(MP3)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("HOOK: dee dee dee dee / doo doo doo  + Hummm + DROP@20s")
    print(MP3)


if __name__ == "__main__":
    main()
