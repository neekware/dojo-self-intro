#!/usr/bin/env python3
"""02 code: picture (IDE push → mic pull) + two-part Eve VO, pause between on dissolve."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/02.00.00-stt-talk"
PIC = SEC / "video/final/LOCKED-02-code-picture.mp4"
VO1 = SEC / "audio/final/code-vo-part1.mp3"
VO2 = SEC / "audio/final/code-vo-part2.mp3"
AWORK = SEC / "audio/work"
OUT = SEC / "video/final/LOCKED-02-stt.mp4"

# Picture: ~13.6s. IDE push ~0–6.6, dissolve ~6.6, mic pull begins ~6.9.
# Part1 rides the IDE PUSH (starts early). Part2 rides the PULL-OUT (starts after it begins).
P1_START = 0.4            # part1 over the IDE push-in
PART2_START = 7.2         # part2 begins just after the pull-out starts
TAIL_PAD = 0.4            # minimal hold after part2 ends (avoid long freeze)


def probe(path: Path) -> float:
    return float(
        subprocess.check_output(
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
    )


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd[:8]), "...")
    subprocess.check_call(cmd)


def main() -> None:
    for p in (PIC, VO1, VO2):
        if not p.exists():
            raise SystemExit(f"missing {p}")
    AWORK.mkdir(parents=True, exist_ok=True)

    pic_d = probe(PIC)
    v1 = probe(VO1)
    v2 = probe(VO2)

    # Part1 rides push, Part2 rides pull-out. If part1 would overrun the pull-out
    # start, push part2 just after part1 ends so lines never overlap.
    p2_start = max(PART2_START, P1_START + v1 + 0.6)
    # End right after VO; do NOT stretch to full picture (that caused the freeze).
    total = p2_start + v2 + TAIL_PAD

    # If VO would run past the picture, gently speed the picture (setpts) so its
    # motion lasts exactly `total` — no frozen hold, motion runs to the end.
    speed = pic_d / total if total < pic_d else 1.0
    stretch = total / pic_d if total > pic_d else 1.0  # >1 → slow picture to fill
    print(f"picture stretch factor={stretch:.3f} (>1 slows motion to fill VO)")
    print(f"pic={pic_d:.2f} v1={v1:.2f} v2={v2:.2f} p1@{P1_START:.2f} p2@{p2_start:.2f} total={total:.2f}")

    d1 = int(round(P1_START * 1000))
    d2 = int(round(p2_start * 1000))

    mixed = AWORK / "code-vo-mix.m4a"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(VO1),
            "-i",
            str(VO2),
            "-filter_complex",
            (
                f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                f"adelay={d1}|{d1},apad[a1];"
                f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                f"adelay={d2}|{d2},apad[a2];"
                f"[a1][a2]amix=inputs=2:normalize=0,"
                f"atrim=0:{total:.3f},asetpts=PTS-STARTPTS[a]"
            ),
            "-map",
            "[a]",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(mixed),
        ]
    )

    # Fill to `total` by SLOWING the picture motion (setpts), not freezing a hold.
    if abs(stretch - 1.0) > 0.01:
        vf = f"setpts={stretch:.5f}*PTS"
    else:
        vf = "null"

    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(PIC),
            "-i",
            str(mixed),
            "-filter_complex",
            f"[0:v]{vf},fps=24,format=yuv420p,setsar=1[v]",
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
            "-movflags",
            "+faststart",
            str(OUT),
        ]
    )

    print("OUT", OUT, probe(OUT))


if __name__ == "__main__":
    main()
