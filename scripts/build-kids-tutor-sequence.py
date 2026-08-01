#!/usr/bin/env python3
"""Build kids-tutor sequence: girl cam → equation+VO → access control+VO."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC = ROOT / "public/sections/14.00.00-kids-tutor"
ARTV = Path("/Users/val/.dojo/workspace/artifacts/ads-b9196c98/video-gen")
VID = SEC / "video"
FINAL = VID / "final"
FINAL.mkdir(parents=True, exist_ok=True)

GIRL = ARTV / "kids-cam-behind-to-side-video_0ms961etz_9e4f2b04.mp4"
EQ = ARTV / "kids-equation-zoom-video_0ms962y7d_992c7515.mp4"
AC = ARTV / "kids-access-control-zoom-video_0ms964dxf_614fb742.mp4"
A_EQ = SEC / "audio/01-quadratic-explain.mp3"
A_AC = SEC / "audio/02-parental-control-line.mp3"
XFADE = 0.7


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


def center_mux(video: Path, audio: Path, dest: Path) -> Path:
    vdur = probe(video)
    adur = probe(audio)
    delay = max(0, int(((vdur - adur) / 2) * 1000))
    fc = (
        f"[1:a]aresample=48000,aformat=channel_layouts=stereo,"
        f"adelay={delay}|{delay},apad=whole_dur={vdur}[a]"
    )
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-i",
            str(audio),
            "-filter_complex",
            fc,
            "-map",
            "0:v:0",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-t",
            str(vdur),
            "-movflags",
            "+faststart",
            str(dest),
        ]
    )
    print("mux", dest.name, f"v={vdur:.2f} a={adur:.2f} delay_ms={delay}")
    return dest


def normalize_silent(src: Path, dest: Path) -> Path:
    # ensure stereo silent or keep existing audio
    subprocess.check_call(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=48000",
            "-shortest",
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "17",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-movflags",
            "+faststart",
            str(dest),
        ]
    )
    return dest


def xfade_chain(paths: list[Path], dest: Path) -> None:
    tmp = Path(tempfile.mkdtemp(prefix="kids-xf-"))
    try:
        norms = []
        for i, p in enumerate(paths):
            n = tmp / f"n{i}.mp4"
            subprocess.check_call(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(p),
                    "-vf",
                    "fps=24,scale=1280:720:force_original_aspect_ratio=decrease,"
                    "pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "17",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-ar",
                    "48000",
                    "-ac",
                    "2",
                    "-movflags",
                    "+faststart",
                    str(n),
                ]
            )
            norms.append(n)
            print("norm", n.name, probe(n))

        durs = [probe(p) for p in norms]
        n = len(norms)
        offsets = [0.0]
        for i in range(1, n):
            offsets.append(offsets[-1] + durs[i - 1] - XFADE)

        inputs: list[str] = []
        for p in norms:
            inputs += ["-i", str(p)]
        v = "[0:v]null[v0];"
        a = "[0:a]anull[a0];"
        for i in range(1, n):
            v += f"[v{i-1}][{i}:v]xfade=transition=fade:duration={XFADE}:offset={offsets[i]:.4f}[v{i}];"
            a += f"[a{i-1}][{i}:a]acrossfade=d={XFADE}:c1=tri:c2=tri[a{i}];"
        last = n - 1
        subprocess.check_call(
            [
                "ffmpeg",
                "-y",
                *inputs,
                "-filter_complex",
                v + a,
                "-map",
                f"[v{last}]",
                "-map",
                f"[a{last}]",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "17",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "aac",
                "-b:a",
                "192k",
                "-movflags",
                "+faststart",
                str(dest),
            ]
        )
        print("MASTER", dest, probe(dest))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> None:
    shutil.copy2(GIRL, VID / "01-girl-behind-to-side.mp4")
    shutil.copy2(EQ, VID / "02-equation-zoom-raw.mp4")
    shutil.copy2(AC, VID / "03-access-zoom-raw.mp4")

    girl = normalize_silent(GIRL, FINAL / "01-girl-behind-to-side.mp4")
    eq = center_mux(EQ, A_EQ, FINAL / "02-equation-with-vo.mp4")
    ac = center_mux(AC, A_AC, FINAL / "03-access-with-vo.mp4")

    master = FINAL / "kids-tutor-sequence.mp4"
    xfade_chain([girl, eq, ac], master)
    shutil.copy2(master, VID / "04-kids-tutor-sequence.mp4")


if __name__ == "__main__":
    main()
