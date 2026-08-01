#!/usr/bin/env python3
"""Assemble the master reel in ONE encode — no generational loss.

The cumulative builder re-encoded the whole timeline on every join (25 passes),
so early sections went through 25 generations of compression. This script joins
every section in a single filtergraph and encodes exactly once at high quality.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "public/sections"
OUT = S / "15.00.00-final/video/final/DOJO-REEL-MASTER.mp4"

FADE = 0.300        # incoming dissolve between sections
CARD_HOLD = 1.500

W, H, FPS = 1920, 1080, 30

# High-quality single encode
ENC = [
    "-c:v", "libx264", "-preset", "slow", "-crf", "16",
    "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2",
    "-x264-params", "ref=4:bframes=3:aq-mode=2",
    "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2",
    "-movflags", "+faststart",
]

NORM_V = (f"scale={W}:{H}:flags=lanczos:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS},format=yuv420p")

# (card_png | None, section_master)
# Standalone LOCKED masters only — no intermediate cumulatives (regenerable, low quality).
TIMELINE: list[tuple[str | None, str]] = [
    (None, "00.00.00-brand/video/final/LOCKED-00-brand-open.mp4"),
    (None, "01.00.00-what-is-dojo/video/final/LOCKED-01-what-is-dojo.mp4"),
    ("02.00.00-stt-talk/after/final/title-card-talk.png",
     "02.00.00-stt-talk/video/final/LOCKED-02-stt.mp4"),
    ("02.10.00-tts-listen/after/final/title-card-listen.png",
     "02.10.00-tts-listen/video/final/LOCKED-03-woman-arc-opener.mp4"),
    (None, "02.10.00-tts-listen/video/final/LOCKED-03-tts-listen.mp4"),
    (None, "02.10.00-tts-listen/video/final/LOCKED-03-ears-listen.mp4"),
    ("02.20.00-lane-assist/after/final/title-card-coding-lane-assist.png",
     "02.20.00-lane-assist/video/final/LOCKED-lane-assist.mp4"),
    ("02.30.00-more-than-coding/after/final/title-card-multimedia-powerhouse.png",
     "02.30.00-more-than-coding/video/final/LOCKED-02.30-more-than-coding.mp4"),
    ("03.00.00-tryon/after/final/title-card-fashion-tryon.png",
     "03.00.00-tryon/video/final/LOCKED-03-tryon.mp4"),
    ("04.00.00-architecture-hq/after/final/title-card-architecture.png",
     "04.00.00-architecture-hq/video/final/LOCKED-04-architecture.mp4"),
    ("05.00.00-dojox-combine/after/final/title-card-product-combine.png",
     "05.00.00-dojox-combine/video/final/LOCKED-05-product-combine.mp4"),
    (None, "06.00.00-dojox-coffee/video/final/LOCKED-06-coffee.mp4"),
    (None, "07.00.00-dojox-perfume/video/final/LOCKED-07-perfume.mp4"),
    (None, "09.00.00-promo-motion/video/final/LOCKED-09-promo.mp4"),
    (None, "09.10.00-lipsync/video/final/LOCKED-09.10-lipsync.mp4"),
    (None, "12.00.00-character-life/video/final/LOCKED-12-characters.mp4"),
    (None, "13.00.00-multilingual/video/final/LOCKED-13-multilingual.mp4"),
    (None, "13.10.00-diagrams-equations/video/final/LOCKED-13.10-diagrams-equations.mp4"),
    (None, "14.00.00-kids-tutor/video/final/LOCKED-14-kids-tutor.mp4"),
    (None, "15.00.00-final/video/final/LOCKED-15-final.mp4"),
]


def run(cmd: list[str], quiet: bool = True) -> None:
    subprocess.run(cmd, check=True,
                   stdout=subprocess.DEVNULL if quiet else None,
                   stderr=subprocess.DEVNULL if quiet else None)


def dur(p: Path) -> float:
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)], text=True).strip())


def stream_dur(p: Path, stream: str) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", stream,
         "-show_entries", "stream=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)], text=True).strip()
    try:
        return float(out.splitlines()[0])
    except (ValueError, IndexError):
        return dur(p)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="dojo-master-") as td:
        tmp = Path(td)

        # Render each card once as a lossless intermediate
        segments: list[Path] = []
        for i, (card_rel, master_rel) in enumerate(TIMELINE):
            if card_rel:
                card_png = S / card_rel
                if not card_png.exists():
                    raise SystemExit(f"missing card: {card_png}")
                card_mp4 = tmp / f"card-{i:02d}.mp4"
                run([
                    "ffmpeg", "-y", "-loglevel", "error",
                    "-loop", "1", "-t", f"{CARD_HOLD:.3f}", "-i", str(card_png),
                    "-f", "lavfi", "-t", f"{CARD_HOLD:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
                    "-filter_complex",
                    f"[0:v]{NORM_V},setpts=PTS-STARTPTS[v];"
                    "[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a]",
                    "-map", "[v]", "-map", "[a]", "-t", f"{CARD_HOLD:.3f}",
                    "-c:v", "libx264", "-preset", "ultrafast", "-qp", "0",
                    "-pix_fmt", "yuv420p", "-c:a", "pcm_s16le", "-f", "matroska",
                    str(card_mp4),
                ])
                segments.append(card_mp4)

            master = S / master_rel
            if not master.exists():
                raise SystemExit(f"missing master: {master}")
            segments.append(master)

        n = len(segments)
        print(f"{n} segments, single-pass encode")

        inputs: list[str] = []
        for seg in segments:
            inputs += ["-i", str(seg)]

        # Normalize every segment. Some masters have a video stream slightly
        # shorter than their audio (multilingual is 0.344s short) — clone the
        # last frame out to the full segment length so nothing freezes early.
        seg_len = [dur(s) for s in segments]
        parts = ""
        for i, seg in enumerate(segments):
            v_end = stream_dur(seg, "v:0")
            gap = seg_len[i] - v_end
            pad = (f"tpad=stop_mode=clone:stop_duration={gap + 0.05:.3f},"
                   f"trim=0:{seg_len[i]:.3f}," if gap > 0.005 else "")
            if gap > 0.005:
                print(f"  pad {seg.name}: video short by {gap:.3f}s")
            parts += (
                f"[{i}:v]{NORM_V},setpts=PTS-STARTPTS,{pad}setpts=PTS-STARTPTS[v{i}];"
                f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                f"asetpts=PTS-STARTPTS[a{i}];"
            )

        # Chain xfades: outgoing preserved in full, incoming fades in over FADE
        chain = ""
        prev_v, prev_a = "v0", "a0"
        offset = seg_len[0]
        for i in range(1, n):
            vlab, alab = f"cv{i}", f"ca{i}"
            chain += (
                f"[{prev_v}]tpad=stop_mode=clone:stop_duration={FADE}[p{i}];"
                f"[{prev_a}][a{i}]concat=n=2:v=0:a=1[{alab}];"
                f"[p{i}][v{i}]xfade=transition=fade:duration={FADE}:"
                f"offset={offset:.6f}[{vlab}];"
            )
            offset += seg_len[i]
            prev_v, prev_a = vlab, alab

        # Single loudness normalization at the end
        filt = (parts + chain +
                f"[{prev_v}]null[v];"
                f"[{prev_a}]loudnorm=I=-14:TP=-1.0:LRA=11[a]")

        OUT.parent.mkdir(parents=True, exist_ok=True)
        print("encoding master (single pass, crf 16)...")
        run(["ffmpeg", "-y", "-loglevel", "error", *inputs,
             "-filter_complex", filt,
             "-map", "[v]", "-map", "[a]", *ENC, str(OUT)], quiet=False)

    print(f"\nOUT {OUT}")
    print(f"duration {dur(OUT):.3f}s")


if __name__ == "__main__":
    main()
