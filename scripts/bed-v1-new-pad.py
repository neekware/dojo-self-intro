#!/usr/bin/env python3
"""
Keep v1 stems minus old pad; add a soft non-humming replacement pad.
"""

from __future__ import annotations

import math
import subprocess
import wave
from array import array
from pathlib import Path

STEMS = Path(__file__).resolve().parents[1] / "public/sections/00.00.00-brand/audio/stems-v1"
OUT = Path(__file__).resolve().parents[1] / "public/sections/00.00.00-brand/audio"
WAV = OUT / "dojo-bed-instrumental.wav"
MP3 = OUT / "dojo-bed-instrumental.mp3"
PAD_WAV = STEMS / "pad-soft-new.wav"

SR = 44100
BPM = 92
BEAT = 60.0 / BPM


def clamp(x, a=-1.0, b=1.0):
    return a if x < a else b if x > b else x


def sine(f, t, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


class LPF:
    def __init__(self, fc):
        self.y = 0.0
        self.a = math.exp(-2 * math.pi * fc / SR)

    def __call__(self, x):
        self.y = (1 - self.a) * x + self.a * self.y
        return self.y


def read_wav(p: Path):
    with wave.open(str(p), "rb") as w:
        n = w.getnframes()
        samp = array("h")
        samp.frombytes(w.readframes(n))
    return [s / 32768.0 for s in samp]


def write_float_wav(path: Path, samples: list[float]) -> None:
    peak = max(1e-9, max(abs(s) for s in samples))
    g = 0.9 / peak
    out = array("h")
    for s in samples:
        y = math.tanh(s * g * 1.04)
        out.append(int(clamp(y) * 32767))
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(out.tobytes())


def main() -> None:
    keep = ["kick", "hat", "snare", "pluck", "bass"]
    stems = {name: read_wav(STEMS / f"{name}.wav") for name in keep}
    n = len(stems["kick"])
    DUR = n / SR

    # --- NEW PAD: soft airy chords, NO high shimmer, NO slow siren LFO ---
    # Warm closed voicings, long crossfades, dark lowpass, tiny slow breath only on amp
    chords = [
        # mid-low only (Hz) — avoid 400Hz+ drones that hum
        [130.81, 164.81, 196.00],  # C E G
        [145.83, 174.61, 220.00],  # D F A-ish soft
        [98.00, 123.47, 146.83],  # G B D
        [110.00, 130.81, 164.81],  # A C E
    ]
    # hold each chord longer = less motion fatigue
    chord_sec = 4 * 4 * BEAT  # 4 bars ~ 10.4s
    pad = [0.0] * n
    lp = LPF(700)  # quite dark — silky not buzzy
    lp2 = LPF(500)

    for i in range(n):
        t = i / SR
        x = t / chord_sec
        i0 = int(math.floor(x)) % len(chords)
        i1 = (i0 + 1) % len(chords)
        frac = x - math.floor(x)
        # long stable hold, short smooth crossfade
        if frac < 0.82:
            w0, w1 = 1.0, 0.0
        else:
            u = (frac - 0.82) / 0.18
            u = u * u * (3 - 2 * u)
            w0, w1 = 1.0 - u, u

        s = 0.0
        for w, ci in ((w0, i0), (w1, i1)):
            if w <= 1e-6:
                continue
            ch = chords[ci]
            for j, f in enumerate(ch):
                # pure sine stack only — no 2x octave sparkle (that hummed)
                amp = 0.20 if j == 0 else 0.14
                # very slight stereo-less detune via phase
                s += w * amp * sine(f, t, j * 0.7)
        # amplitude breath only, very slow, tiny
        breath = 0.92 + 0.08 * sine(0.03, t)
        y = lp2(lp(s)) * 0.26 * breath
        pad[i] = y

    write_float_wav(PAD_WAV, pad)

    # mix keep stems + new pad
    mix = [0.0] * n
    for data in stems.values():
        for i, v in enumerate(data):
            mix[i] += v
    for i, v in enumerate(pad):
        mix[i] += v

    # fades
    fade = int(0.8 * SR)
    for i in range(fade):
        mix[i] *= i / fade
        mix[n - 1 - i] *= i / fade

    write_float_wav(WAV, mix)
    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(WAV), "-c:a", "libmp3lame", "-b:a", "192k", str(MP3)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    # labeled copy
    labeled = OUT / "dojo-bed-v1-soft-pad.mp3"
    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(WAV), "-c:a", "libmp3lame", "-b:a", "192k", str(labeled)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("new soft pad + v1 keep stems (no old pad)")
    print(MP3)


if __name__ == "__main__":
    main()
