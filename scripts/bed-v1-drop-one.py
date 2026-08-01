#!/usr/bin/env python3
"""
Recreate first bed (v1) as stems, then mix with ONE stem dropped.
Round 1 drop: PLUCK MOTIF (the periodic dee-doo / bright insert).
"""

from __future__ import annotations

import math
import subprocess
import wave
from array import array
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "public/sections/00.00.00-brand/audio"
STEMS = OUT / "stems-v1"
WAV = OUT / "dojo-bed-instrumental.wav"
MP3 = OUT / "dojo-bed-instrumental.mp3"
# also label this experiment
EXP_MP3 = OUT / "dojo-bed-v1-minus-pluck.mp3"

SR = 44100
BPM = 92
BEAT = 60.0 / BPM
DUR = 64.0
N = int(SR * DUR)

# Which stem to drop this round:
DROP = "pluck"  # options: pad, kick, hat, snare, pluck, bass


def clamp(x, a=-1.0, b=1.0):
    return a if x < a else b if x > b else x


def sine(f, t, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def tri(f, t):
    x = (t * f) % 1.0
    return 2 * abs(2 * x - 1) - 1


def noise(i):
    x = math.sin(i * 12.9898) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


def env(t, a=0.01, d=0.12, s=0.65, r=0.35, hold=0.4):
    if t < 0:
        return 0.0
    if t < a:
        return t / a
    if t < a + d:
        return 1.0 - (1.0 - s) * ((t - a) / d)
    if t < a + d + hold:
        return s
    if t < a + d + hold + r:
        return s * (1.0 - ((t - a - d - hold) / r))
    return 0.0


def write_wav(path: Path, samples: array) -> None:
    # samples float -1..1
    out = array("h")
    peak = max(1e-9, max(abs(s) for s in samples))
    g = 0.9 / peak
    for s in samples:
        y = math.tanh(s * g * 1.05)
        out.append(int(clamp(y) * 32767))
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(out.tobytes())


def main() -> None:
    STEMS.mkdir(parents=True, exist_ok=True)

    pad = array("f", [0.0] * N)
    kick = array("f", [0.0] * N)
    hat = array("f", [0.0] * N)
    snare = array("f", [0.0] * N)
    pluck = array("f", [0.0] * N)
    bass = array("f", [0.0] * N)

    chords = [
        [220.00, 261.63, 329.63, 440.00],
        [174.61, 220.00, 261.63, 349.23],
        [130.81, 164.81, 196.00, 261.63],
        [196.00, 246.94, 293.66, 392.00],
    ]
    roots = [110.0, 87.31, 65.41, 98.0]
    sec_per_chord = 2 * 4 * BEAT

    # pads
    for i in range(N):
        t = i / SR
        ci = int(t / sec_per_chord) % 4
        local = t % sec_per_chord
        pad_e = 0.55 + 0.45 * math.sin(2 * math.pi * local / sec_per_chord - math.pi / 2)
        s = 0.0
        for j, f in enumerate(chords[ci]):
            s += 0.22 * sine(f, t) * (0.7 if j else 1.0)
            s += 0.08 * tri(f * 0.5, t)
        s += 0.05 * sine(chords[ci][2] * 2, t) * math.sin(2 * math.pi * 0.1 * t)
        pad[i] = s * 0.22 * pad_e

    # kick
    for beat_i in range(int(DUR / BEAT) + 2):
        if beat_i % 2 != 0:
            continue
        start = beat_i * BEAT
        strong = (beat_i % 4) in (0, 2)
        for k in range(int(0.18 * SR)):
            idx = int((start + k / SR) * SR)
            if idx >= N:
                break
            tt = k / SR
            f = 90 * math.exp(-tt * 18) + 40
            body = math.sin(2 * math.pi * f * tt) * math.exp(-tt * 14)
            kick[idx] += body * (0.28 if strong else 0.14)

    # hats
    for beat_i in range(int(DUR / (BEAT / 2)) + 2):
        start = beat_i * (BEAT / 2)
        for k in range(int(0.04 * SR)):
            idx = int((start + k / SR) * SR)
            if idx >= N:
                break
            tt = k / SR
            h = noise(idx) * math.exp(-tt * 90)
            amp = 0.035 if (beat_i % 2 == 0) else 0.02
            hat[idx] += h * amp

    # snare ghosts
    for beat_i in range(int(DUR / BEAT) + 2):
        if beat_i % 4 not in (1, 3):
            continue
        start = beat_i * BEAT
        for k in range(int(0.12 * SR)):
            idx = int((start + k / SR) * SR)
            if idx >= N:
                break
            tt = k / SR
            nse = noise(idx + 99) * math.exp(-tt * 28)
            tone = sine(180, tt) * math.exp(-tt * 20) * 0.3
            snare[idx] += (nse * 0.7 + tone) * 0.09

    # pluck motif (CANDIDATE TO DROP)
    motif = [0, 2, 4, 7, 4, 2]
    scale = [220.00, 246.94, 261.63, 293.66, 329.63, 349.23, 392.00, 440.00]
    for bar in range(int(DUR / (4 * BEAT))):
        base = bar * 4 * BEAT
        for mi, deg in enumerate(motif):
            st = base + mi * (BEAT / 2)
            f = scale[deg % len(scale)]
            for k in range(int(0.35 * SR)):
                idx = int((st + k / SR) * SR)
                if idx >= N:
                    break
                tt = k / SR
                e = env(tt, a=0.005, d=0.08, s=0.25, r=0.2, hold=0.05)
                pl = (0.7 * sine(f, tt) + 0.3 * sine(f * 2, tt)) * e
                pluck[idx] += pl * 0.07

    # bass
    for i in range(N):
        t = i / SR
        ci = int(t / sec_per_chord) % 4
        local = t % BEAT
        e = env(local, a=0.01, d=0.08, s=0.5, r=0.15, hold=0.25)
        b = sine(roots[ci], t) * 0.55 + sine(roots[ci] * 2, t) * 0.15
        bass[i] = b * e * 0.16

    stems = {
        "pad": pad,
        "kick": kick,
        "hat": hat,
        "snare": snare,
        "pluck": pluck,
        "bass": bass,
    }

    # write all stems for future rounds
    for name, st in stems.items():
        write_wav(STEMS / f"{name}.wav", st)

    # mix all except DROP
    mix = array("f", [0.0] * N)
    for name, st in stems.items():
        if name == DROP:
            continue
        for i in range(N):
            mix[i] += st[i]

    # fades like original
    fade = int(0.8 * SR)
    for i in range(fade):
        mix[i] *= i / fade
        mix[N - 1 - i] *= i / fade

    write_wav(WAV, mix)
    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(WAV), "-c:a", "libmp3lame", "-b:a", "192k", str(MP3)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    subprocess.check_call(
        ["ffmpeg", "-y", "-i", str(WAV), "-c:a", "libmp3lame", "-b:a", "192k", str(EXP_MP3)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # also full mix reference
    full = array("f", [0.0] * N)
    for st in stems.values():
        for i in range(N):
            full[i] += st[i]
    for i in range(fade):
        full[i] *= i / fade
        full[N - 1 - i] *= i / fade
    write_wav(STEMS / "full-mix.wav", full)

    print(f"DROPPED stem: {DROP}")
    print(f"playing mix without: {DROP}")
    print(f"stems in {STEMS}")
    print(MP3)


if __name__ == "__main__":
    main()
