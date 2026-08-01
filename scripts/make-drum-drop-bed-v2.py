#!/usr/bin/env python3
"""
Clean drum + drop bed v2.
No rising hum, no bright zing, solid pocket. 94 BPM.
"""

from __future__ import annotations

import math
import subprocess
import wave
from array import array
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parents[1] / "public/sections/00.00.00-brand/audio"
WAV = OUT_DIR / "dojo-bed-drums-drop.wav"
MP3 = OUT_DIR / "dojo-bed-drums-drop.mp3"
# archive previous
OLD = OUT_DIR / "dojo-bed-drums-drop-v1-bad.mp3"

SR = 44100
BPM = 94
BEAT = 60.0 / BPM
DUR = 48.0
N = int(SR * DUR)


def clamp(x, a=-1.0, b=1.0):
    return a if x < a else b if x > b else x


def sine(f, t, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def noise(i):
    x = math.sin(i * 127.1 + 311.7) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


class OnePole:
    def __init__(self, fc):
        self.y = 0.0
        self.set(fc)

    def set(self, fc):
        self.a = math.exp(-2 * math.pi * clamp(fc, 20, SR * 0.4) / SR)

    def __call__(self, x):
        self.y = x + self.a * (self.y - x)
        return self.y


def exp_env(t, decay):
    return math.exp(-t * decay) if t >= 0 else 0.0


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if MP3.exists() and not OLD.exists():
        MP3.rename(OLD)

    buf = array("f", [0.0] * N)

    # Static warm chords — NO sweeps, NO rising partials, long holds
    # Am - F - C - G loop, 4 bars each (slow)
    chord_fs = [
        [110.0, 164.81, 220.0, 261.63],
        [87.31, 130.81, 174.61, 220.0],
        [65.41, 98.0, 130.81, 196.0],
        [98.0, 123.47, 146.83, 196.0],
    ]
    bass_f = [55.0, 43.65, 32.7, 49.0]
    bars_hold = 4
    chord_sec = bars_hold * 4 * BEAT

    lp_pad = OnePole(900)   # dark pad — no harsh highs
    lp_bass = OnePole(140)
    lp_hat = OnePole(5500)  # dark hats
    lp_master = OnePole(7500)

    # ---- PAD (constant, filtered, no shimmer octaves) ----
    for i in range(N):
        t = i / SR
        ci = int(t / chord_sec) % 4
        # crossfade last 12% of chord
        phase = (t / chord_sec) - math.floor(t / chord_sec)
        c0, c1 = ci, (ci + 1) % 4
        if phase < 0.88:
            w0, w1 = 1.0, 0.0
        else:
            u = (phase - 0.88) / 0.12
            u = u * u * (3 - 2 * u)
            w0, w1 = 1 - u, u
        s = 0.0
        for w, c in ((w0, c0), (w1, c1)):
            if w <= 0:
                continue
            for j, f in enumerate(chord_fs[c]):
                # fundamentals only + tiny 1.5 for warmth, NO 2x sparkle
                s += w * (0.16 if j < 2 else 0.10) * sine(f, t, j)
                if j == 0:
                    s += w * 0.04 * sine(f * 1.5, t)
        # slow breath only (very slow — not a hum sweep)
        breath = 0.9 + 0.1 * sine(0.04, t)
        buf[i] += lp_pad(s) * 0.30 * breath

    # ---- BASS (locked notes, no slides) ----
    for i in range(N):
        t = i / SR
        ci = int(t / chord_sec) % 4
        phase = (t / chord_sec) - math.floor(t / chord_sec)
        c0, c1 = ci, (ci + 1) % 4
        if phase < 0.88:
            f = bass_f[c0]
        else:
            u = (phase - 0.88) / 0.12
            u = u * u * (3 - 2 * u)
            # short crossfade in amp domain not pitch glide — two basses
            f = bass_f[c0]  # stay on note; second added below
        local = t % BEAT
        e = 1.0
        if local < 0.015:
            e = local / 0.015
        elif local > 0.45:
            e = max(0.35, 1.0 - (local - 0.45) / 0.2)

        # sidechain duck
        duck = 0.5 + 0.5 * min(1.0, (local / BEAT) * 5) if local < BEAT * 0.2 else 1.0

        b = sine(f, t) * 0.85 + sine(f * 2, t) * 0.08
        if phase >= 0.88:
            u = (phase - 0.88) / 0.12
            u = u * u * (3 - 2 * u)
            b = b * (1 - u) + (sine(bass_f[c1], t) * 0.85) * u

        # arrangement
        if t < 8:
            g = 0.55
        elif 16 <= t < 20:
            g = 0.85
        elif 20 <= t < 36:
            g = 1.0
        else:
            g = 0.75
        buf[i] += lp_bass(b) * e * 0.36 * g * duck

    # ---- KICK ----
    for bi in range(int(DUR / BEAT) + 2):
        start = bi * BEAT
        # intro: half-time; drop: 4-on-floor; else 1&3
        if start < 8 and bi % 2:
            continue
        if 8 <= start < 20 and bi % 2:
            continue
        # 20-36: every beat
        # after 36: 1&3
        if start >= 36 and bi % 2:
            continue

        for k in range(int(0.22 * SR)):
            idx = int(start * SR) + k
            if idx >= N:
                break
            tt = k / SR
            # short pitch drop, stays LOW (no whistle)
            f = 58 * math.exp(-tt * 14) + 36
            body = math.sin(2 * math.pi * f * tt) * math.exp(-tt * 10)
            # almost no click
            click = noise(idx) * math.exp(-tt * 180) * 0.04
            amp = 0.48 if start >= 20 else 0.38
            if start < 8:
                amp = 0.28
            buf[idx] += (body + click) * amp

    # ---- SNARE 2&4 ----
    for bi in range(int(DUR / BEAT) + 2):
        if bi % 4 not in (1, 3):
            continue
        start = bi * BEAT
        if start < 4:
            continue
        amp = 0.12 if start < 20 else 0.18
        if start >= 36:
            amp = 0.12
        for k in range(int(0.12 * SR)):
            idx = int(start * SR) + k
            if idx >= N:
                break
            tt = k / SR
            nse = lp_hat(noise(idx + 11)) * math.exp(-tt * 28)
            tone = sine(170, tt) * math.exp(-tt * 22) * 0.25
            buf[idx] += (nse * 0.65 + tone) * amp

    # ---- HATS (dark) ----
    for bi in range(int(DUR / (BEAT / 2)) + 2):
        start = bi * (BEAT / 2)
        if start < 2:
            continue
        amp = 0.022 if bi % 2 == 0 else 0.012
        if 20 <= start < 36:
            amp *= 1.3
        if start < 8:
            amp *= 0.6
        for k in range(int(0.025 * SR)):
            idx = int(start * SR) + k
            if idx >= N:
                break
            tt = k / SR
            h = lp_hat(noise(idx + 5)) * math.exp(-tt * 90)
            buf[idx] += h * amp

    # 16ths only in drop, very quiet
    for bi in range(int(DUR / (BEAT / 4)) + 2):
        start = bi * (BEAT / 4)
        if not (20 <= start < 34):
            continue
        if bi % 2 == 0:
            continue
        for k in range(int(0.015 * SR)):
            idx = int(start * SR) + k
            if idx >= N:
                break
            tt = k / SR
            h = lp_hat(noise(idx + 9)) * math.exp(-tt * 110)
            buf[idx] += h * 0.012

    # ---- pre-drop: level + snare roll (NO noise riser sweep) ----
    # snare roll 18.5 - 20
    for bi in range(24):
        start = 18.5 + bi * (0.06 - bi * 0.0008)
        if start >= 20:
            break
        for k in range(int(0.05 * SR)):
            idx = int(start * SR) + k
            if idx >= N:
                break
            tt = k / SR
            nse = lp_hat(noise(idx + 40 + bi)) * math.exp(-tt * 40)
            buf[idx] += nse * (0.04 + 0.01 * bi / 24)

    # ---- DROP IMPACT (sub + short body, no crash sizzle) ----
    for k in range(int(0.5 * SR)):
        idx = int(20 * SR) + k
        if idx >= N:
            break
        tt = k / SR
        boom = sine(48 * math.exp(-tt * 2.5), tt) * math.exp(-tt * 3.5)
        body = sine(70, tt) * math.exp(-tt * 8) * 0.35
        buf[idx] += boom * 0.55 + body * 0.25

    # ---- DROP stab chords (rhythmic, fixed pitches — not rising) ----
    stab_chords = [
        [130.81, 155.56, 196.0],
        [174.61, 220.0, 261.63],
    ]
    for bar in range(int(DUR / (4 * BEAT))):
        base = bar * 4 * BEAT
        if base < 20 or base >= 36:
            continue
        ch = stab_chords[bar % 2]
        for hit in (0.0, 1.0, 2.5):
            st = base + hit * BEAT
            for k in range(int(0.2 * SR)):
                idx = int(st * SR) + k
                if idx >= N:
                    break
                tt = k / SR
                e = math.exp(-tt * 12) if tt > 0.01 else tt / 0.01
                s = 0.0
                for f in ch:
                    s += sine(f, tt) * 0.2
                buf[idx] += s * e * 0.12

    # arrangement mute pad a bit on drop so drums punch
    for i in range(int(20 * SR), min(N, int(36 * SR))):
        # already mixed; slight overall ok
        pass

    # fades
    for i in range(int(0.4 * SR)):
        buf[i] *= (i / (0.4 * SR)) ** 1.3
    for i in range(int(1.2 * SR)):
        buf[N - 1 - i] *= (i / (1.2 * SR)) ** 1.1

    peak = max(1e-9, max(abs(v) for v in buf))
    g = 0.86 / peak
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
    print("wrote", MP3, f"bpm={BPM} drop@20s clean")


if __name__ == "__main__":
    main()
