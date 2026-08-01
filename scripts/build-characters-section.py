#!/usr/bin/env python3
"""Build the CHARACTERS chapter.

CHARACTERS card + VO over the dragon still, then three clips:
dragon alive -> portrait alive -> lipsync talk (its own audio kept).
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "public/sections"
LIFE = S / "12.00.00-character-life"
VOICE = S / "08.00.00-character-voice"
LIP = S / "09.10.00-lipsync"

OUT = LIFE / "video/final/LOCKED-12-characters.mp4"
CARD = LIFE / "after/final/title-card-character-life.png"
VO = LIFE / "audio/final/characters-eve-vo.mp3"

# Show BOTH stills first (VO over them), then bring BOTH to life in the same order.
STILLS = [
    LIFE / "before/01-blue-dragon-fullbody.png",
    VOICE / "before/01-portrait-still.jpg",
]

CLIPS = [
    LIFE / "video/01-blue-dragon-alive.mp4",
    VOICE / "video/01-portrait-alive.mp4",
]

CARD_HOLD = 1.500
PAD_IN = 0.250
PAD_OUT = 0.400
FADE = 0.300
STILL_GAP = 0.450   # black beat separating the stills block from the animations

NORM_V = ("scale=1920:1080:flags=lanczos:force_original_aspect_ratio=decrease,"
          "pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p")
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart"]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def dur(p: Path) -> float:
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)], text=True).strip())


def vdur(p: Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)], text=True).strip()
    try:
        return float(out)
    except ValueError:
        return dur(p)


def norm(src: Path, out: Path) -> None:
    run(["ffmpeg", "-y", "-i", str(src),
         "-filter_complex",
         f"[0:v]{NORM_V},setpts=PTS-STARTPTS[v];"
         "[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a]",
         "-map", "[v]", "-map", "[a]", *ENC, str(out)])


def join(base: Path, incoming: Path, out: Path) -> None:
    off = vdur(base)
    run(["ffmpeg", "-y", "-i", str(base), "-i", str(incoming),
         "-filter_complex",
         f"[0:v]format=yuv420p,fps=30,setsar=1,setpts=PTS-STARTPTS,"
         f"tpad=stop_mode=clone:stop_duration={FADE}[v0h];"
         f"[1:v]format=yuv420p,fps=30,setsar=1,setpts=PTS-STARTPTS[v1];"
         f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];"
         f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS,"
         f"afade=t=in:st=0:d={FADE}[a1];"
         f"[v0h][v1]xfade=transition=fade:duration={FADE}:offset={off:.6f}[v];"
         f"[a0][a1]concat=n=2:v=0:a=1[a]",
         "-map", "[v]", "-map", "[a]", *ENC, str(out)])


def main() -> None:
    for p in (CARD, VO, *STILLS, *CLIPS):
        if not p.exists():
            raise SystemExit(f"missing: {p}")

    vo_d = dur(VO)
    stills_block = PAD_IN + vo_d + PAD_OUT
    per_still = stills_block / len(STILLS)
    stills_end = CARD_HOLD + stills_block
    delay = int((CARD_HOLD + PAD_IN) * 1000)
    print(f"VO={vo_d:.3f} card={CARD_HOLD} per_still={per_still:.3f} end={stills_end:.3f}")

    with tempfile.TemporaryDirectory(prefix="dojo-chars-") as td:
        tmp = Path(td)

        cur = tmp / "stills.mp4"
        inputs: list[str] = ["-loop", "1", "-t", f"{CARD_HOLD:.3f}", "-i", str(CARD)]
        for s in STILLS:
            inputs += ["-loop", "1", "-t", f"{per_still:.3f}", "-i", str(s)]
        inputs += ["-i", str(VO)]

        n = len(STILLS) + 1
        parts = "".join(f"[{i}:v]{NORM_V},setpts=PTS-STARTPTS[v{i}];" for i in range(n))
        chain = "".join(f"[v{i}]" for i in range(n))

        run([
            "ffmpeg", "-y", *inputs,
            "-filter_complex",
            f"{parts}{chain}concat=n={n}:v=1:a=0[v];"
            f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"adelay={delay}|{delay},apad,atrim=0:{stills_end:.3f},asetpts=PTS-STARTPTS[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{stills_end:.3f}", *ENC, str(cur),
        ])

        # Clear break so the audience reads stills as stills, then sees them move.
        gap = tmp / "gap.mp4"
        run([
            "ffmpeg", "-y",
            "-f", "lavfi", "-t", f"{STILL_GAP:.3f}", "-i", "color=c=black:s=1920x1080:r=30",
            "-f", "lavfi", "-t", f"{STILL_GAP:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
            "-filter_complex",
            "[0:v]format=yuv420p,setsar=1[v];"
            "[1:a]aformat=sample_rates=48000:channel_layouts=stereo[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{STILL_GAP:.3f}", *ENC, str(gap),
        ])
        gapped = tmp / "stills-gap.mp4"
        join(cur, gap, gapped)
        cur = gapped

        for i, clip in enumerate(CLIPS, 1):
            n = tmp / f"clip-{i}.mp4"
            norm(clip, n)
            nxt = tmp / f"chain-{i}.mp4"
            print(f"join {i}: +{clip.name}")
            join(cur, n, nxt)
            cur = nxt

        OUT.parent.mkdir(parents=True, exist_ok=True)
        run(["ffmpeg", "-y", "-i", str(cur), "-c", "copy", str(OUT)])

    print(f"OUT {OUT} {dur(OUT):.3f}s")


if __name__ == "__main__":
    main()
