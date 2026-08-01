#!/usr/bin/env python3
"""Build the closing montage: capability clips enter one at a time in a grid.

Tiles pop in sequentially over the outro VO, then the whole grid settles and
fades to black.
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
S = ROOT / "public/sections"
SEC = S / "15.00.00-final"
OUT = SEC / "video/final/LOCKED-15-final.mp4"
VO = SEC / "audio/final/final-outro-vo.mp3"

W, H = 1920, 1080
COLS, ROWS = 4, 3
TW, TH = W // COLS, H // ROWS   # 480 x 360

PAD_IN = 0.500
PAD_OUT = 1.600
FADE_OUT = 1.200
SLOWMO = 1.6   # gentle slow motion; tiles hold in place
ENTRY_SPAN = 5.5   # all 12 tiles are in within ~5.5s

# Closing torii splash + download CTA
SPLASH = S / "00.00.00-brand/after/final/splash-LOCKED.png"
CTA_VO = SEC / "audio/final/final-download-cta-vo.mp3"
CTA_PAD_IN = 0.600
CTA_PAD_OUT = 2.200
SPLASH_FADE = 0.500

# Finale card opens the section; torii splash is the last frame of the reel
FINALE_CARD = SEC / "after/final/title-card-meet-the-future.png"
CARD_HOLD = 1.800

# 12 raw capability clips — the most vivid moment of each, no cards or stills
SOURCES = [
    S / "02.20.00-lane-assist/after/final/code-ide-dojo-LOCKED.jpg",   # code (slow zoom) TOP-LEFT
    S / "12.00.00-character-life/video/01-blue-dragon-alive.mp4",      # blue dragon
    S / "02.10.00-tts-listen/video/final/LOCKED-03-tts-listen.mp4",    # eye
    S / "03.00.00-tryon/video/01-dress-walk.mp4",                      # try-on walk
    S / "04.00.00-architecture-hq/video/01-flyover.mp4",               # flyover
    S / "09.10.00-lipsync/video/01-lipsync-talk.mp4",                  # lip sync
    S / "07.00.00-dojox-perfume/video/01-perfume-orbit.mp4",           # perfume orbit
    S / "09.00.00-promo-motion/video/01-headphones-promo.mp4",         # promo
    S / "08.00.00-character-voice/video/01-portrait-alive.mp4",        # portrait alive
    S / "02.20.00-lane-assist/video/work/LOCKED-lane-assist-phone-only.mp4",  # lane assist
    S / "02.00.00-stt-talk/video/final/LOCKED-02-stt.mp4",             # talk to Dojo
    S / "02.10.00-tts-listen/video/final/LOCKED-03-ears-listen.mp4",   # ears
]

# Seek to the most vivid moment of each source
SEEKS = [0.0, 1.2, 4.5, 1.5, 3.0, 2.5, 2.0, 2.0, 1.5, 3.5, 9.0, 4.0]

ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart"]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def dur(p: Path) -> float:
    return float(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(p)], text=True).strip())


def main() -> None:
    clips = [p for p in SOURCES if p.exists()]
    if len(clips) < len(SOURCES):
        missing = [p.name for p in SOURCES if not p.exists()]
        print(f"WARNING missing {len(missing)}: {missing}")
    if not VO.exists():
        raise SystemExit(f"missing VO: {VO}")

    vo_d = dur(VO)
    total = PAD_IN + vo_d + PAD_OUT
    n = len(clips)

    # Stagger entrances so every tile is up within ENTRY_SPAN
    entry_window = min(ENTRY_SPAN, vo_d * 0.9)
    step = entry_window / n
    entries = [PAD_IN + i * step for i in range(n)]
    fade_st = max(0.0, total - FADE_OUT)

    print(f"VO={vo_d:.3f} total={total:.3f} tiles={n} step={step:.3f}")

    # Each tile plays in slow motion from its seek point and never restarts.
    # Still images become a slow Ken Burns push-in instead.
    src_needed = total / SLOWMO
    inputs: list[str] = []
    is_still: list[bool] = []
    for clip, seek in zip(clips, SEEKS):
        still = clip.suffix.lower() in {".jpg", ".jpeg", ".png"}
        is_still.append(still)
        if still:
            inputs += ["-loop", "1", "-t", f"{total:.3f}", "-i", str(clip)]
        else:
            loop_seek = min(seek, max(0.0, dur(clip) - src_needed - 0.2))
            inputs += ["-ss", f"{loop_seek:.3f}", "-t", f"{src_needed + 0.2:.3f}",
                       "-i", str(clip)]
    inputs += ["-i", str(VO)]

    zoom_frames = int(total * 30)
    parts = [f"color=c=black:s={W}x{H}:r=30:d={total:.3f},format=yuv420p[bg];"]
    for i in range(n):
        if is_still[i]:
            # supersample then integer-centered zoompan = no shake
            parts.append(
                f"[{i}:v]scale={TW * 4}:{TH * 4}:force_original_aspect_ratio=increase,"
                f"crop={TW * 4}:{TH * 4},setsar=1,fps=30,format=yuv420p,"
                f"zoompan=z='min(1+0.14*on/{zoom_frames},1.14)':"
                f"x='trunc(iw/2-(iw/zoom/2))':y='trunc(ih/2-(ih/zoom/2))':"
                f"d={zoom_frames}:s={TW * 2}x{TH * 2}:fps=30,"
                f"scale={TW}:{TH}:flags=lanczos,"
                f"trim=0:{total:.3f},setpts=PTS-STARTPTS,"
                f"fade=t=in:st=0:d=0.400[t{i}];"
            )
        else:
            parts.append(
                f"[{i}:v]scale={TW}:{TH}:force_original_aspect_ratio=increase,"
                f"crop={TW}:{TH},setsar=1,fps=30,format=yuv420p,"
                f"setpts={SLOWMO}*PTS,"
                f"tpad=stop_mode=clone:stop_duration={total:.3f},"
                f"trim=0:{total:.3f},setpts=PTS-STARTPTS,"
                f"fade=t=in:st=0:d=0.400[t{i}];"
            )

    chain = ""
    prev = "bg"
    for i in range(n):
        col, row = i % COLS, i // COLS
        x, y = col * TW, row * TH
        label = f"o{i}"
        chain += (f"[{prev}][t{i}]overlay=x={x}:y={y}:"
                  f"enable='gte(t,{entries[i]:.3f})'[{label}];")
        prev = label

    filt = ("".join(parts) + chain +
            f"[{prev}]fade=t=out:st={fade_st:.3f}:d={FADE_OUT}[v];"
            f"[{n}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"adelay={int(PAD_IN * 1000)}|{int(PAD_IN * 1000)},apad,"
            f"atrim=0:{total:.3f},asetpts=PTS-STARTPTS,"
            f"afade=t=out:st={fade_st:.3f}:d={FADE_OUT}[a]")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="dojo-final-") as td:
        tmp = Path(td)
        montage = tmp / "montage.mp4"
        run(["ffmpeg", "-y", *inputs, "-filter_complex", filt,
             "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}", *ENC, str(montage)])

        # Closing torii splash with the download call-to-action
        cta_d = dur(CTA_VO)
        splash_total = CTA_PAD_IN + cta_d + CTA_PAD_OUT
        splash_fade = max(0.0, splash_total - FADE_OUT)
        cta_delay = int(CTA_PAD_IN * 1000)
        print(f"CTA={cta_d:.3f} splash={splash_total:.3f}")

        splash = tmp / "splash.mp4"
        run([
            "ffmpeg", "-y",
            "-loop", "1", "-t", f"{splash_total:.3f}", "-i", str(SPLASH),
            "-i", str(CTA_VO),
            "-filter_complex",
            f"[0:v]scale={W}:{H}:flags=lanczos:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p,"
            f"setpts=PTS-STARTPTS[v];"
            f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"adelay={cta_delay}|{cta_delay},apad,atrim=0:{splash_total:.3f},"
            f"asetpts=PTS-STARTPTS,afade=t=out:st={splash_fade:.3f}:d=0.600[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{splash_total:.3f}", *ENC, str(splash),
        ])

        # Finale card opens this section
        card = tmp / "card.mp4"
        run([
            "ffmpeg", "-y",
            "-loop", "1", "-t", f"{CARD_HOLD:.3f}", "-i", str(FINALE_CARD),
            "-f", "lavfi", "-t", f"{CARD_HOLD:.3f}", "-i", "anullsrc=r=48000:cl=stereo",
            "-filter_complex",
            f"[0:v]scale={W}:{H}:flags=lanczos:force_original_aspect_ratio=decrease,"
            f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p,"
            f"setpts=PTS-STARTPTS[v];"
            f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{CARD_HOLD:.3f}", *ENC, str(card),
        ])

        carded = tmp / "card-montage.mp4"
        run([
            "ffmpeg", "-y", "-i", str(card), "-i", str(montage),
            "-filter_complex",
            f"[0:v]format=yuv420p,fps=30,setsar=1,setpts=PTS-STARTPTS,"
            f"tpad=stop_mode=clone:stop_duration={SPLASH_FADE}[v0h];"
            f"[1:v]format=yuv420p,fps=30,setsar=1,setpts=PTS-STARTPTS[v1];"
            f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];"
            f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d={SPLASH_FADE}[a1];"
            f"[v0h][v1]xfade=transition=fade:duration={SPLASH_FADE}:offset={CARD_HOLD:.6f}[v];"
            f"[a0][a1]concat=n=2:v=0:a=1[a]",
            "-map", "[v]", "-map", "[a]", *ENC, str(carded),
        ])

        carded_d = dur(carded)
        run([
            "ffmpeg", "-y", "-i", str(carded), "-i", str(splash),
            "-filter_complex",
            f"[0:v]format=yuv420p,fps=30,setsar=1,setpts=PTS-STARTPTS,"
            f"tpad=stop_mode=clone:stop_duration={SPLASH_FADE}[v0h];"
            f"[1:v]format=yuv420p,fps=30,setsar=1,setpts=PTS-STARTPTS[v1];"
            f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[a0];"
            f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS,"
            f"afade=t=in:st=0:d={SPLASH_FADE}[a1];"
            f"[v0h][v1]xfade=transition=fade:duration={SPLASH_FADE}:offset={carded_d:.6f}[v];"
            f"[a0][a1]concat=n=2:v=0:a=1[a]",
            "-map", "[v]", "-map", "[a]", *ENC, str(OUT),
        ])

    print(f"OUT {OUT} {dur(OUT):.3f}s")


if __name__ == "__main__":
    main()
