#!/usr/bin/env python3
"""Instrumental drum + drop bed for Dojo showcase (~92 BPM feel, no vocals)."""

from __future__ import annotations

import math
import struct
import subprocess
import wave
from array import array
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[1] / "public/sections/00.00.00-brand/audio"
WAV = OUT_DIR / "dojo-bed-drums-drop.wav"
MP3 = OUT_DIR / "dojo-bed-drums-drop.mp3"

SR = 44100
BPM = 96
BEAT = 60.0 / BPM
DUR = 48.0  # seconds, loop-friendly
N = int(SR * DUR)


def clamp(x: float, a: float = -1.0, b: float = 1.0) -> float:
    return a if x < a else b if x > b else x


def sine(f: float, t: float, ph: float = 0.0) -> float:
    return math.sin(2 * math.pi * f * t + ph)


def noise(i: int) -> float:
    x = math.sin(i * 12.9898 + 78.233) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


class LPF:
    def __init__(self, fc: float):
        self.y = 0.0
        self.set(fc)

    def set(self, fc: float) -> None:
        self.a = math.exp(-2 * math.pi * clamp(fc, 30, SR * 0.45) / SR)

    def __call__(self, x: float) -> float:
        self.y = (1 - self.a) * x + self.a * self.y
        return self.y


def env_adsr(t: float, a: float, d: float, s: float, r: float, hold: float) -> float:
    if t < 0:
        return 0.0
    if t < a:
        return t / max(a, 1e-6)
    if t < a + d:
        return 1.0 - (1.0 - s) * ((t - a) / max(d, 1e-6))
    if t < a + d + hold:
        return s
    if t < a + d + hold + r:
        return s * (1.0 - (t - a - d - hold) / max(r, 1e-6))
    return 0.0


def section_gain(t: float) -> tuple[float, float, float, float]:
    """
    Returns (drums, bass, pad, lead) gains by arrangement.
    0-8s: build (light drums)
    8-16s: groove
    16-20s: pre-drop filter build
    20-32s: DROP
    32-40s: groove B
    40-48s: outro / soft
    """
    if t < 8:
        return 0.45, 0.55, 0.7, 0.15
    if t < 16:
        return 0.85, 0.85, 0.65, 0.35
    if t < 20:
        # pre-drop tension
        u = (t - 16) / 4
        return 0.7 + 0.2 * u, 0.9, 0.5, 0.2 + 0.5 * u
    if t < 32:
        return 1.0, 1.0, 0.55, 0.85
    if t < 40:
        return 0.9, 0.9, 0.6, 0.5
    u = (t - 40) / 8
    return 0.55 * (1 - 0.5 * u), 0.6 * (1 - 0.4 * u), 0.7, 0.2 * (1 - u)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    buf = array("f", [0.0] * N)

    # harmonic beds
    chords = [
        [130.81, 164.81, 196.00, 261.63],  # Cm
        [174.61, 220.00, 261.63, 349.23],  # F
        [196.00, 246.94, 293.66, 392.00],  # G
        [146.83, 174.61, 220.00, 293.66],  # Dmbassy
    ]
    roots = [65.41, 87.31, 98.00, 73.42]
    sec_ch = 4 * BEAT * 2  # 2 bars

    lpf_pad = LPF(1800)
    lpf_bass = LPF(160)
    lpf_hat = LPF(9000)
    lpf_master = LPF(12000)
    lpf_build = LPF(400)

    # --- pads ---
    for i in range(N):
        t = i / SR
        ci = int(t / sec_ch) % len(chords)
        g_dr, g_ba, g_pa, g_le = section_gain(t)
        s = 0.0
        for j, f in enumerate(chords[ci]):
            s += (0.18 if j < 2 else 0.12) * sine(f, t, j * 0.3)
        breath = 0.85 + 0.15 * sine(0.07, t)
        # pre-drop darker
        if 16 <= t < 20:
            lpf_pad.set(600 + 2000 * ((t - 16) / 4))
        elif t >= 20:
            lpf_pad.set(2200)
        else:
            lpf_pad.set(1600)
        buf[i] += lpf_pad(s) * 0.28 * g_pa * breath

    # --- bass ---
    for i in range(N):
        t = i / SR
        g_dr, g_ba, g_pa, g_le = section_gain(t)
        ci = int(t / sec_ch) % len(roots)
        f = roots[ci]
        local = t % BEAT
        e = env_adsr(local, 0.01, 0.06, 0.55, 0.12, 0.28)
        # sidechain-ish duck on kick beats
        kphase = (t % BEAT) / BEAT
        duck = 0.55 + 0.45 * min(1.0, kphase * 4) if kphase < 0.25 else 1.0
        b = sine(f, t) * 0.75 + sine(f * 2, t) * 0.12
        if t >= 20:  # drop: more sub
            b += sine(f * 0.5, t) * 0.25
        buf[i] += lpf_bass(b) * e * 0.34 * g_ba * duck

    # --- drums ---
    # kick on 1 & 3 always; on drop also 4-on-floor
    for bi in range(int(DUR / BEAT) + 3):
        start = bi * BEAT
        t0 = start
        g_dr, _, _, _ = section_gain(t0 + 0.01)
        four = t0 >= 20 and t0 < 40
        if not four and (bi % 2 != 0):
            continue
        for k in range(int(0.2 * SR)):
            idx = int((start + k / SR) * SR)
            if idx >= N:
                break
            tt = k / SR
            f = (95 if four else 85) * math.exp(-tt * 16) + 40
            body = math.sin(2 * math.pi * f * tt) * math.exp(-tt * 11)
            click = noise(idx) * math.exp(-tt * 140) * 0.12
            buf[idx] += (body * 0.9 + click) * 0.42 * g_dr

    # snare/clap 2 & 4
    for bi in range(int(DUR / BEAT) + 3):
        if bi % 4 not in (1, 3):
            continue
        start = bi * BEAT
        g_dr, _, _, _ = section_gain(start + 0.01)
        if start < 4:  # sparse intro
            g_dr *= 0.35
        for k in range(int(0.15 * SR)):
            idx = int((start + k / SR) * SR)
            if idx >= N:
                break
            tt = k / SR
            nse = lpf_hat(noise(idx + 20)) * math.exp(-tt * 24)
            tone = sine(180, tt) * math.exp(-tt * 20) * 0.35
            snap = noise(idx + 99) * math.exp(-tt * 60) * 0.4
            buf[idx] += (nse * 0.55 + tone + snap * 0.3) * 0.22 * g_dr

    # hats 8ths; 16ths on drop
    step = BEAT / 2
    for bi in range(int(DUR / step) + 4):
        start = bi * step
        g_dr, _, _, _ = section_gain(start + 0.01)
        # 16ths in drop
        if 20 <= start < 36:
            # extra off-16
            pass
        amp = 0.05 if bi % 2 == 0 else 0.028
        if 20 <= start < 36:
            amp *= 1.25
        if start < 8:
            amp *= 0.5
        for k in range(int(0.03 * SR)):
            idx = int((start + k / SR) * SR)
            if idx >= N:
                break
            tt = k / SR
            h = lpf_hat(noise(idx + 3)) * math.exp(-tt * 85)
            buf[idx] += h * amp * g_dr

    if True:
        # 16th hats in drop
        step16 = BEAT / 4
        for bi in range(int(DUR / step16) + 4):
            start = bi * step16
            if not (20 <= start < 36):
                continue
            if bi % 2 == 0:
                continue  # already have 8ths
            for k in range(int(0.02 * SR)):
                idx = int((start + k / SR) * SR)
                if idx >= N:
                    break
                tt = k / SR
                h = lpf_hat(noise(idx + 8)) * math.exp(-tt * 100)
                buf[idx] += h * 0.02

    # tom fill into drop (19.0-20.0)
    fill_notes = [0.0, 0.25, 0.5, 0.625, 0.75, 0.875]
    fill_f = [120, 140, 160, 180, 200, 220]
    for nf, ff in zip(fill_notes, fill_f):
        start = 19.0 + nf * 1.0
        for k in range(int(0.12 * SR)):
            idx = int((start + k / SR) * SR)
            if 0 <= idx < N:
                tt = k / SR
                tom = sine(ff * math.exp(-tt * 6), tt) * math.exp(-tt * 14)
                buf[idx] += tom * 0.2

    # riser noise into drop 16-20
    for i in range(int(16 * SR), min(N, int(20.05 * SR))):
        t = i / SR
        u = (t - 16) / 4
        nse = noise(i) * (0.02 + 0.1 * u * u)
        # rising HPF feel via subtractive
        lpf_build.set(300 + 6000 * u * u)
        buf[i] += (nse - lpf_build(nse)) * 0.9

    # impact at drop
    for k in range(int(0.4 * SR)):
        idx = int(20 * SR) + k
        if idx >= N:
            break
        tt = k / SR
        boom = sine(55 * math.exp(-tt * 3), tt) * math.exp(-tt * 4)
        crash = noise(idx) * math.exp(-tt * 6) * 0.35
        buf[idx] += boom * 0.45 + crash * 0.2

    # lead stab motif on drop (not a rising hum — rhythmic)
    scale = [261.63, 311.13, 349.23, 392.00, 466.16]  # C Eb F G Bb
    pattern = [0, 2, 3, 2, 4, 3, 2, 0]
    for bar in range(int(DUR / (4 * BEAT))):
        base = bar * 4 * BEAT
        g_dr, g_ba, g_pa, g_le = section_gain(base + 0.05)
        if g_le < 0.2:
            continue
        for mi, deg in enumerate(pattern):
            st = base + mi * (BEAT / 2)
            if st < 20 and st > 8:
                # light only
                amp = 0.04 * g_le
            elif st >= 20:
                amp = 0.09 * g_le
            else:
                continue
            f = scale[deg % len(scale)]
            for k in range(int(0.22 * SR)):
                idx = int((st + k / SR) * SR)
                if idx >= N:
                    break
                tt = k / SR
                e = env_adsr(tt, 0.005, 0.05, 0.3, 0.1, 0.04)
                pl = sine(f, tt) * 0.8 + sine(f * 1.5, tt) * 0.1
                buf[idx] += pl * e * amp

    # master fades
    fade_in = int(0.5 * SR)
    fade_out = int(1.5 * SR)
    for i in range(fade_in):
        buf[i] *= (i / fade_in) ** 1.2
    for i in range(fade_out):
        buf[N - 1 - i] *= (i / fade_out) ** 1.1

    # normalize + soft clip
    peak = max(1e-9, max(abs(v) for v in buf))
    g = 0.88 / peak
    lpf_master.set(11000)
    out = array("h")
    for v in buf:
        y = lpf_master(v * g)
        y = math.tanh(y * 1.1)
        out.append(int(clamp(y) * 32767))

    with wave.open(str(WAV), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(out.tobytes())

    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(WAV), "-c:a", "libmp3lame", "-q:a", "2", str(MP3)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("wrote", MP3)
    print(f"bpm={BPM} dur={DUR}s drop@20s")


if __name__ == "__main__":
    main()
