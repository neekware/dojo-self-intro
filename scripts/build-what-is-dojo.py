#!/usr/bin/env python3
"""01.00.00-what-is-dojo standalone master.

PIPELINE (audio-safe):
  1) Build SILENT picture segments (giants zoom + gem loop)
  2) Stitch video with slow xfade (video only — no acrossfade)
  3) Lay dry VOs on the timeline with adelay (full level, nothing eaten)

Giants VO occupies the giants hold.
Gem VO starts AFTER the crossfade completes so the woman section keeps
every word at full level.
"""

from __future__ import annotations

import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/01.00.00-what-is-dojo"
CRED = ROOT / "public/sections/17.00.00-credits"
GIANTS_STILL = CRED / "after/final/credits-LOCKED-1920.jpg"
GIANTS_VO = CRED / "audio/final/credits-giants-vo.mp3"
PICTURE = SEC / "video/final/LOCKED-01-connection.mp4"
GEM_VO = SEC / "audio/final/what-is-dojo-gem-vo.mp3"
WORK = SEC / "video/work"
AUDIO_WORK = SEC / "audio/work"
OUT = SEC / "video/final/LOCKED-01-what-is-dojo.mp4"

# Giants hold timing (match credits hold style)
G_PAD_IN = 0.70
G_PAD_OUT = 1.30
G_ZOOM_END = 1.12

# After join completes: hold picture in silence, THEN start gem VO
GEM_PAUSE_AFTER_STITCH = 1.00  # breath after blur-cut before woman VO
GEM_PAD_IN = 0.0
GEM_PAD_OUT = 1.30

# Blur-veil hard cut (NOT a dissolve of two sharp frames):
#   blur both ends + dissolve under blur (no hard-cut bump)
# Giants → gem: ramp into blur, dissolve WHILE blurred (no hard cut bump), ramp out.
BLUR_RAMP = 0.25   # sharp→blur on giants end; blur→sharp on gem start
BLUR_XFADE = 0.40  # dissolve between the two fully-blurred streams (kills the bump)
BLUR_SIGMA = 24.0
FPS = 30


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
    subprocess.check_call(cmd)


def main() -> None:
    for p, label in [
        (GIANTS_STILL, "giants still"),
        (GIANTS_VO, "giants VO"),
        (PICTURE, "gem picture"),
        (GEM_VO, "gem VO"),
    ]:
        if not p.exists():
            raise SystemExit(f"missing {label}: {p}")

    WORK.mkdir(parents=True, exist_ok=True)
    AUDIO_WORK.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)

    g_vo = probe(GIANTS_VO)
    gem_vo = probe(GEM_VO)
    pic_dur = probe(PICTURE)

    # --- 1a) SILENT giants Ken Burns ---
    g_hold = G_PAD_IN + g_vo + G_PAD_OUT
    g_frames = int(round(g_hold * FPS))
    z_expr = f"1+{(G_ZOOM_END - 1.0):.6f}*on/{max(g_frames - 1, 1)}"
    giants_silent = WORK / "giants-silent.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(GIANTS_STILL),
            "-vf",
            (
                f"scale=8000:-1,"
                f"zoompan=z='{z_expr}':"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d=1:s=1920x1080:fps={FPS},"
                f"format=yuv420p,setsar=1"
            ),
            "-t",
            f"{g_hold:.3f}",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            str(giants_silent),
        ]
    )

    # --- 1b) SILENT gem loop: blur-side + pause + full gem VO + pad ---
    # No xfade overlap — hard cut under blur, so gem length is full tail after cut.
    blur_bridge = BLUR_RAMP + BLUR_XFADE  # edge material on each side
    gem_tail = GEM_PAUSE_AFTER_STITCH + GEM_PAD_IN + gem_vo + GEM_PAD_OUT
    gem_silent_dur = blur_bridge + gem_tail
    loops = max(1, int(math.ceil(gem_silent_dur / pic_dur)) + 1)
    gem_silent = WORK / "gem-silent.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-stream_loop",
            str(loops),
            "-i",
            str(PICTURE),
            "-vf",
            (
                f"trim=duration={gem_silent_dur:.3f},setpts=PTS-STARTPTS,"
                f"fps={FPS},format=yuv420p,setsar=1"
            ),
            "-an",
            "-t",
            f"{gem_silent_dur:.3f}",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            str(gem_silent),
        ]
    )

    g_d = probe(giants_silent)
    gem_d = probe(gem_silent)
    if g_d <= blur_bridge + 0.05 or gem_d <= blur_bridge + 0.05:
        raise SystemExit(f"blur bridge too long for segs {g_d:.2f}/{gem_d:.2f}")

    # --- 2) VIDEO ONLY: blur both ends + dissolve UNDER blur (no hard-cut bump) ---
    # A sharp | 0.25s →blur | 0.40s blurred dissolve A→B | 0.25s blur→ | B sharp
    s = BLUR_SIGMA
    r = BLUR_RAMP
    x = BLUR_XFADE
    bridge = r + x  # seconds pulled from each clip edge
    # Mid dissolve overlaps x seconds
    expected_v = g_d + gem_d - x
    video_only = WORK / "what-is-dojo-video-only.mp4"
    fc = (
        f"[0:v]fps={FPS},format=yuv420p,setsar=1,setpts=PTS-STARTPTS,split=2[asrc][asrc2];"
        f"[asrc]trim=0:{g_d - bridge:.3f},setpts=PTS-STARTPTS[ah];"
        f"[asrc2]trim=start={g_d - bridge:.3f},setpts=PTS-STARTPTS,split=2[ae0][ae1];"
        f"[ae0]null[ae_s];"
        f"[ae1]gblur=sigma={s:.1f}:steps=3[ae_b];"
        # A edge: sharp→blur over r, then stays blurred for x
        f"[ae_s][ae_b]xfade=transition=fade:duration={r:.3f}:offset=0[ae];"
        f"[1:v]fps={FPS},format=yuv420p,setsar=1,setpts=PTS-STARTPTS,split=2[bsrc][bsrc2];"
        f"[bsrc]trim=0:{bridge:.3f},setpts=PTS-STARTPTS,split=2[be0][be1];"
        f"[be0]gblur=sigma={s:.1f}:steps=3[be_b];"
        f"[be1]null[be_s];"
        # B edge: blurred for x, then blur→sharp over r
        f"[be_b][be_s]xfade=transition=fade:duration={r:.3f}:offset={x:.3f}[be];"
        f"[bsrc2]trim=start={bridge:.3f},setpts=PTS-STARTPTS[bh];"
        # Dissolve the two blurred edges into each other (kills the bump)
        f"[ae][be]xfade=transition=fade:duration={x:.3f}:offset={r:.3f}[mid];"
        f"[ah][mid][bh]concat=n=3:v=1:a=0,format=yuv420p[v]"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(giants_silent),
            "-i",
            str(gem_silent),
            "-filter_complex",
            fc,
            "-map",
            "[v]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-t",
            f"{expected_v:.3f}",
            "-movflags",
            "+faststart",
            str(video_only),
        ]
    )
    v_dur = probe(video_only)

    # --- 3) AUDIO timeline (no acrossfade) ---
    # Giants VO: starts at G_PAD_IN
    # Gem VO after join settles to sharp gem + pause
    # join ends at (g_d - bridge) + (2*r + x) = g_d + r
    g_delay_ms = int(round(G_PAD_IN * 1000))
    gem_start = g_d + r + GEM_PAUSE_AFTER_STITCH + GEM_PAD_IN
    gem_delay_ms = int(round(gem_start * 1000))

    # Build mixed stereo bed to exact video length
    mixed = AUDIO_WORK / "what-is-dojo-vo-mix.m4a"
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(GIANTS_VO),
            "-i",
            str(GEM_VO),
            "-filter_complex",
            (
                f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                f"adelay={g_delay_ms}|{g_delay_ms},apad[g];"
                f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                f"adelay={gem_delay_ms}|{gem_delay_ms},apad[m];"
                f"[g][m]amix=inputs=2:duration=longest:dropout_transition=0,"
                f"atrim=0:{v_dur:.3f},alimiter=limit=0.95[a]"
            ),
            "-map",
            "[a]",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-t",
            f"{v_dur:.3f}",
            str(mixed),
        ]
    )

    # --- 4) Mux ---
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_only),
            "-i",
            str(mixed),
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            "-movflags",
            "+faststart",
            str(OUT),
        ]
    )

    out_d = probe(OUT)
    print(
        f"giants_silent={g_d:.3f}s gem_silent={gem_d:.3f}s "
        f"ramp={BLUR_RAMP}s xfade_under_blur={BLUR_XFADE}s sigma={BLUR_SIGMA}"
    )
    print(f"video_only={v_dur:.3f}s expected≈{expected_v:.3f}s (hard cut under blur)")
    print(
        f"giants_vo@{G_PAD_IN:.2f}s  pause_after_stitch={GEM_PAUSE_AFTER_STITCH:.2f}s  "
        f"gem_vo@{gem_start:.2f}s"
    )
    print(f"OUT={out_d:.3f}s", OUT, OUT.stat().st_size)
    if abs(out_d - v_dur) > 0.2:
        raise SystemExit(f"mux duration mismatch out={out_d} video={v_dur}")


if __name__ == "__main__":
    main()
